#!/usr/bin/env python3
import csv
import datetime as dt
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text


OPTION_RE = re.compile(r"^([A-Z]+)(\d{6})([CP])(\d{8})$")
ZERO = Decimal("0")
OPTION_MULTIPLIER = Decimal("100")
STOCK_MULTIPLIER = Decimal("1")
EXPIRATION_TIME = dt.time(23, 59, 59)
EXPIRE_SIDE = "Expire"


@dataclass(frozen=True)
class Trade:
    seq: int
    timestamp: dt.datetime
    instrument: str
    match_key: str
    asset: str
    option_kind: str
    side: str
    qty: Decimal
    price: Decimal
    multiplier: Decimal
    expiry: Optional[dt.date] = None


@dataclass(frozen=True)
class Lot:
    side: str
    qty: Decimal
    price: Decimal


@dataclass(frozen=True)
class ReportRow:
    timestamp: dt.datetime
    instrument: str
    asset: str
    option_kind: str
    side: str
    qty: Decimal
    price: Decimal
    closed_qty: Decimal
    realized: Decimal
    running: Decimal


@dataclass(frozen=True)
class PositionRow:
    instrument: str
    asset: str
    option_kind: str
    side: str
    qty: Decimal
    avg_price: Decimal
    expiry: Optional[dt.date]


def parse_time(value: str) -> Optional[dt.datetime]:
    if not value:
        return None
    text = value.strip()
    parts = text.split()
    if parts and parts[-1].isalpha() and len(parts[-1]) <= 4:
        text = " ".join(parts[:-1])
    try:
        return dt.datetime.strptime(text, "%m/%d/%Y %H:%M:%S")
    except ValueError:
        return None


def parse_decimal(value: str) -> Optional[Decimal]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.startswith("@"):
        text = text[1:]
    text = text.replace(",", "")
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def parse_option_symbol(symbol: str):
    match = OPTION_RE.match(symbol.strip().upper())
    if not match:
        return None
    root, yymmdd, call_put, strike_raw = match.groups()
    exp_date = dt.datetime.strptime(yymmdd, "%y%m%d").date()
    strike = Decimal(str(int(strike_raw))) / Decimal("1000")
    return root, exp_date, call_put, strike


def format_option_date(exp_date: dt.date) -> str:
    return exp_date.strftime("%d %b %Y")


def format_option_display(root: str, exp_date: dt.date, strike: Decimal) -> str:
    strike_text = format_qty(strike)
    return f"{root} {format_option_date(exp_date)} ${strike_text}"


def strategy_kind_from_name(name: str) -> str:
    lowered = name.replace(" ", "").lower()
    if "ironcondor" in lowered:
        return "IronCondor"
    if "condor" in lowered:
        return "Condor"
    if "butterfly" in lowered:
        return "Butterfly"
    if "straddle" in lowered:
        return "Straddle"
    if "strangle" in lowered:
        return "Strangle"
    if "spread" in lowered:
        return "Spread"
    return "Strategy"


def format_qty(qty: Decimal) -> str:
    text = format(qty, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def format_price(value: Decimal, asset: str) -> str:
    if asset.startswith("Option"):
        text = f"{value:.3f}"
    else:
        text = f"{value:.2f}"
    return text.rstrip("0").rstrip(".")


def format_pnl(value: Decimal) -> Text:
    style = "green" if value >= ZERO else "red"
    text = f"{value:+,.2f}"
    return Text(text, style=style)


def format_expiry(expiry: Optional[dt.date]) -> str:
    if not expiry:
        return "-"
    return format_option_date(expiry)


def extract_core_fields(row: dict) -> Optional[tuple[str, Decimal, Decimal, dt.datetime]]:
    status = row.get("Status", "").strip().lower()
    if status and status != "filled":
        return None
    side = row.get("Side", "").strip().title()
    if side not in ("Buy", "Sell"):
        return None
    qty = parse_decimal(row.get("Filled", ""))
    if qty is None or qty <= ZERO:
        return None
    price = parse_decimal(row.get("Avg Price") or row.get("Price"))
    if price is None:
        return None
    time_val = row.get("Filled Time") or row.get("Placed Time") or ""
    timestamp = parse_time(time_val)
    if not timestamp:
        return None
    return side, qty, price, timestamp


def build_strategy_meta(rows: list[dict], parent_times: set[str]) -> dict[str, dict[str, object]]:
    meta: dict[str, dict[str, object]] = {}
    for row in rows:
        placed = row.get("Placed Time", "").strip()
        symbol = row.get("Symbol", "").strip()
        if placed not in parent_times or not symbol:
            continue
        parsed = parse_option_symbol(symbol)
        if not parsed:
            continue
        root, exp_date, call_put, strike = parsed
        entry = meta.setdefault(
            placed,
            {"root": None, "exp_date": None, "legs": []},
        )
        if entry.get("root") is None:
            entry["root"] = root
        if entry.get("exp_date") is None:
            entry["exp_date"] = exp_date
        legs = entry.get("legs")
        if isinstance(legs, list):
            legs.append((call_put, strike))
    return meta


def build_strategy_key(
    name: str,
    option_kind: str,
    root: Optional[str],
    exp_date: Optional[dt.date],
    legs: Optional[list[tuple[str, Decimal]]],
) -> str:
    if not root or not exp_date:
        return f"strategy:{name}"
    key = f"strategy:{option_kind}:{root}:{exp_date.isoformat()}"
    if legs:
        legs_key = ",".join(
            f"{call_put}{format_qty(strike)}"
            for call_put, strike in sorted(legs, key=lambda v: (v[0], v[1]))
        )
        key = f"{key}:{legs_key}"
    return key


def build_strategy_trade(
    seq: int,
    timestamp: dt.datetime,
    name: str,
    side: str,
    qty: Decimal,
    price: Decimal,
    meta: dict[str, object],
) -> Trade:
    option_kind = strategy_kind_from_name(name)
    root = meta.get("root") if isinstance(meta, dict) else None
    exp_date = meta.get("exp_date") if isinstance(meta, dict) else None
    legs = meta.get("legs") if isinstance(meta, dict) else None
    instrument = name
    if root and exp_date:
        instrument = f"{root} {format_option_date(exp_date)}"
    elif root:
        instrument = str(root)
    elif exp_date:
        instrument = f"{name} {format_option_date(exp_date)}"
    match_key = build_strategy_key(name, option_kind, root, exp_date, legs if isinstance(legs, list) else None)
    return Trade(
        seq=seq,
        timestamp=timestamp,
        instrument=instrument,
        match_key=match_key,
        asset="Option Strategy",
        option_kind=option_kind,
        side=side,
        qty=qty,
        price=price,
        multiplier=OPTION_MULTIPLIER,
        expiry=exp_date if isinstance(exp_date, dt.date) else None,
    )


def build_option_trade(
    seq: int,
    timestamp: dt.datetime,
    symbol: str,
    side: str,
    qty: Decimal,
    price: Decimal,
) -> Trade:
    parsed = parse_option_symbol(symbol)
    if parsed:
        root, exp_date, call_put, strike = parsed
        option_kind = "Call" if call_put == "C" else "Put"
        instrument = format_option_display(root, exp_date, strike)
    else:
        exp_date = None
        option_kind = "Option"
        instrument = symbol
    return Trade(
        seq=seq,
        timestamp=timestamp,
        instrument=instrument,
        match_key=f"option:{symbol}",
        asset="Option",
        option_kind=option_kind,
        side=side,
        qty=qty,
        price=price,
        multiplier=OPTION_MULTIPLIER,
        expiry=exp_date,
    )


def build_stock_trade(
    seq: int,
    timestamp: dt.datetime,
    symbol: str,
    side: str,
    qty: Decimal,
    price: Decimal,
) -> Trade:
    return Trade(
        seq=seq,
        timestamp=timestamp,
        instrument=symbol,
        match_key=f"stock:{symbol}",
        asset="Stock",
        option_kind="",
        side=side,
        qty=qty,
        price=price,
        multiplier=STOCK_MULTIPLIER,
        expiry=None,
    )


def parse_csv(path: Path, seq_start: int) -> tuple[list[Trade], int]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return [], seq_start
        fields = {field.strip() for field in reader.fieldnames}
        if "Side" not in fields or "Filled" not in fields:
            return [], seq_start
        rows = list(reader)

    is_options = "Options" in path.name
    parent_times: set[str] = set()
    if is_options:
        for row in rows:
            name = row.get("Name", "").strip()
            symbol = row.get("Symbol", "").strip()
            if name and not symbol:
                placed = row.get("Placed Time", "").strip()
                if placed:
                    parent_times.add(placed)
    strategy_meta = build_strategy_meta(rows, parent_times) if is_options else {}

    trades: list[Trade] = []
    seq = seq_start
    for row in rows:
        core = extract_core_fields(row)
        if not core:
            continue
        side, qty, price, timestamp = core

        if is_options:
            name = row.get("Name", "").strip()
            symbol = row.get("Symbol", "").strip()
            placed = row.get("Placed Time", "").strip()
            if name and not symbol:
                meta = strategy_meta.get(placed, {})
                trades.append(
                    build_strategy_trade(seq, timestamp, name, side, qty, price, meta)
                )
                seq += 1
                continue
            if placed in parent_times and not name:
                continue
            if symbol:
                trades.append(build_option_trade(seq, timestamp, symbol, side, qty, price))
                seq += 1
            continue

        symbol = row.get("Symbol", "").strip()
        if not symbol:
            continue
        trades.append(build_stock_trade(seq, timestamp, symbol, side, qty, price))
        seq += 1

    return trades, seq


def load_trades(data_dir: Path) -> list[Trade]:
    trades: list[Trade] = []
    seq = 0
    for path in sorted(data_dir.rglob("*.csv")):
        parsed, seq = parse_csv(path, seq)
        trades.extend(parsed)
    return trades


def apply_expiration(lots: tuple[Lot, ...], multiplier: Decimal) -> tuple[tuple[Lot, ...], Decimal, Decimal]:
    if not lots:
        return (), ZERO, ZERO
    realized = ZERO
    closed_qty = ZERO
    for lot in lots:
        if lot.side == "Buy":
            realized += (ZERO - lot.price) * lot.qty * multiplier
        else:
            realized += (lot.price - ZERO) * lot.qty * multiplier
        closed_qty += lot.qty
    return (), realized, closed_qty


def apply_to_lots(
    lots: tuple[Lot, ...],
    trade_side: str,
    trade_qty: Decimal,
    trade_price: Decimal,
    multiplier: Decimal,
) -> tuple[tuple[Lot, ...], Decimal, Decimal]:
    remaining = trade_qty
    realized = ZERO
    closed_qty = ZERO
    updated: list[Lot] = []

    for lot in lots:
        if remaining > ZERO and lot.side != trade_side:
            match = min(remaining, lot.qty)
            pnl_per_contract = (lot.price - trade_price) if trade_side == "Buy" else (trade_price - lot.price)
            realized += pnl_per_contract * match * multiplier
            closed_qty += match
            remaining -= match
            leftover = lot.qty - match
            if leftover > ZERO:
                updated.append(Lot(side=lot.side, qty=leftover, price=lot.price))
        else:
            updated.append(lot)

    if remaining > ZERO:
        updated.append(Lot(side=trade_side, qty=remaining, price=trade_price))

    return tuple(updated), realized, closed_qty


def apply_trade(
    positions: dict[str, tuple[Lot, ...]],
    trade: Trade,
) -> tuple[dict[str, tuple[Lot, ...]], Decimal, Decimal]:
    lots = positions.get(trade.match_key, ())
    if trade.side == EXPIRE_SIDE:
        updated_lots, realized, closed_qty = apply_expiration(lots, trade.multiplier)
    else:
        updated_lots, realized, closed_qty = apply_to_lots(
            lots,
            trade.side,
            trade.qty,
            trade.price,
            trade.multiplier,
        )

    if updated_lots == lots:
        return positions, realized, closed_qty

    updated_positions = dict(positions)
    if updated_lots:
        updated_positions[trade.match_key] = updated_lots
    else:
        updated_positions.pop(trade.match_key, None)
    return updated_positions, realized, closed_qty


def build_expiration_trades(trades: list[Trade], as_of_date: dt.date) -> list[Trade]:
    if not trades:
        return []
    max_seq = max(trade.seq for trade in trades)
    seen: dict[str, Trade] = {}
    for trade in trades:
        if trade.expiry is None or trade.expiry > as_of_date:
            continue
        seen.setdefault(trade.match_key, trade)

    expirations: list[Trade] = []
    seq = max_seq + 1
    for trade in seen.values():
        if trade.expiry is None:
            continue
        expiration_time = dt.datetime.combine(trade.expiry, EXPIRATION_TIME)
        expirations.append(
            Trade(
                seq=seq,
                timestamp=expiration_time,
                instrument=trade.instrument,
                match_key=trade.match_key,
                asset=trade.asset,
                option_kind=trade.option_kind,
                side=EXPIRE_SIDE,
                qty=ZERO,
                price=ZERO,
                multiplier=trade.multiplier,
                expiry=trade.expiry,
            )
        )
        seq += 1
    return expirations


def build_trade_index(trades: Iterable[Trade]) -> dict[str, Trade]:
    index: dict[str, Trade] = {}
    for trade in trades:
        index.setdefault(trade.match_key, trade)
    return index


def compute_report(trades: list[Trade], as_of_date: dt.date) -> tuple[list[ReportRow], dict[str, tuple[Lot, ...]], Decimal]:
    all_trades = list(trades)
    all_trades.extend(build_expiration_trades(trades, as_of_date))
    all_trades.sort(key=lambda trade: (trade.timestamp, trade.seq))

    positions: dict[str, tuple[Lot, ...]] = {}
    running = ZERO
    rows: list[ReportRow] = []

    for trade in all_trades:
        positions, realized, closed_qty = apply_trade(positions, trade)
        if trade.side == EXPIRE_SIDE and closed_qty == ZERO:
            continue
        running += realized
        display_qty = closed_qty if trade.side == EXPIRE_SIDE else trade.qty
        rows.append(
            ReportRow(
                timestamp=trade.timestamp,
                instrument=trade.instrument,
                asset=trade.asset,
                option_kind=trade.option_kind or "-",
                side=trade.side,
                qty=display_qty,
                price=trade.price,
                closed_qty=closed_qty,
                realized=realized,
                running=running,
            )
        )

    return rows, positions, running


def build_position_rows(
    positions: dict[str, tuple[Lot, ...]],
    trade_index: dict[str, Trade],
) -> list[PositionRow]:
    rows: list[PositionRow] = []
    for match_key, lots in positions.items():
        if not lots:
            continue
        total_qty = sum((lot.qty for lot in lots), ZERO)
        if total_qty <= ZERO:
            continue
        weighted = sum((lot.price * lot.qty for lot in lots), ZERO)
        avg_price = weighted / total_qty
        trade = trade_index.get(match_key)
        instrument = trade.instrument if trade else match_key
        asset = trade.asset if trade else "-"
        option_kind = trade.option_kind if trade and trade.option_kind else "-"
        expiry = trade.expiry if trade else None
        rows.append(
            PositionRow(
                instrument=instrument,
                asset=asset,
                option_kind=option_kind,
                side=lots[0].side,
                qty=total_qty,
                avg_price=avg_price,
                expiry=expiry,
            )
        )
    rows.sort(key=lambda row: (row.asset, row.instrument, row.side))
    return rows


def build_report_table(rows: list[ReportRow]) -> Table:
    table = Table(title="Realized P&L by Transaction")
    table.add_column("Date", style="cyan", no_wrap=True)
    table.add_column("Instrument")
    table.add_column("Asset")
    table.add_column("Option")
    table.add_column("Side")
    table.add_column("Qty", justify="right")
    table.add_column("Price", justify="right")
    table.add_column("Closed Qty", justify="right")
    table.add_column("Realized P&L", justify="right")
    table.add_column("Running P&L", justify="right")

    for row in rows:
        table.add_row(
            row.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            row.instrument,
            row.asset,
            row.option_kind,
            row.side,
            format_qty(row.qty),
            format_price(row.price, row.asset),
            format_qty(row.closed_qty),
            format_pnl(row.realized),
            format_pnl(row.running),
        )
    return table


def build_positions_table(rows: list[PositionRow]) -> Optional[Table]:
    if not rows:
        return None
    table = Table(title="Open Positions")
    table.add_column("Instrument")
    table.add_column("Asset")
    table.add_column("Option")
    table.add_column("Side")
    table.add_column("Qty", justify="right")
    table.add_column("Avg Price", justify="right")
    table.add_column("Expiry", justify="right")

    for row in rows:
        table.add_row(
            row.instrument,
            row.asset,
            row.option_kind,
            row.side,
            format_qty(row.qty),
            format_price(row.avg_price, row.asset),
            format_expiry(row.expiry),
        )
    return table


def render_report(rows: list[ReportRow], positions: list[PositionRow], running: Decimal) -> None:
    console = Console()
    console.print(build_report_table(rows))
    positions_table = build_positions_table(positions)
    if positions_table:
        console.print(positions_table)
    else:
        console.print("No open positions.")
    console.print("Final realized P&L:", format_pnl(running))


@click.command()
@click.option(
    "--data-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path("data"),
    show_default=True,
)
@click.option(
    "--as-of",
    "as_of",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=dt.date.today().isoformat(),
    show_default="today",
    help="Include expirations on or before this date (YYYY-MM-DD).",
)
def main(data_dir: Path, as_of: dt.datetime) -> None:
    """Generate a realized P&L report from Webull CSV order exports."""
    trades = load_trades(data_dir)
    if not trades:
        click.echo("No trades found.")
        return

    as_of_date = as_of.date() if as_of else dt.date.today()
    rows, positions, running = compute_report(trades, as_of_date)
    trade_index = build_trade_index(trades)
    position_rows = build_position_rows(positions, trade_index)
    render_report(rows, position_rows, running)


if __name__ == "__main__":
    main()
