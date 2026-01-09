# webull-pnl

CLI report for realized P&L from Webull CSV exports.

## Usage

```bash
uv run webull-pnl --data-dir data
```

Include option expirations up to a specific date:

```bash
uv run webull-pnl --data-dir data --as-of 2025-12-19
```

## Export CSVs from Webull Desktop

1. Open Webull Desktop and go to the Account page.
2. In the Orders pane, click History and set the time range.
3. Click the three-dot menu (top right) and choose Export Orders.
4. Send the export to your email, download it, and extract the CSVs.
5. Put the exported `Orders_*.csv` files into a directory (for example `data/`) and pass it to `--data-dir`.

## Example output

```text
$ uv run webull-pnl --data-dir data
   Built webull-pnl @ file:///Users/typon/gitz/webull
Uninstalled 1 package in 0.66ms
Installed 1 package in 1ms
Realized P&L by Transaction
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━┳━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Date                ┃ Instrument              ┃ Asset           ┃ Option     ┃ Side   ┃ Qty ┃  Price ┃ Closed Qty ┃ Realized P&L ┃ Running P&L ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━╇━━━━━╇━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 2025-05-13 11:16:47 │ BYDDY                   │ Stock           │ -          │ Buy    │   9 │ 102.75 │          0 │        +0.00 │       +0.00 │
│ 2025-07-16 10:54:54 │ NVDA 18 Jul 2025        │ Option Strategy │ IronCondor │ Sell   │   1 │   1.41 │          0 │        +0.00 │       +0.00 │
│ 2025-07-16 12:12:46 │ UNH 18 Jul 2025 $290    │ Option          │ Put        │ Buy    │   5 │   2.18 │          0 │        +0.00 │       +0.00 │
│ 2025-07-17 10:03:15 │ UNH 18 Jul 2025 $290    │ Option          │ Put        │ Sell   │   5 │   6.28 │          5 │    +2,050.00 │   +2,050.00 │
│ 2025-07-18 10:54:17 │ NVDA 18 Jul 2025        │ Option Strategy │ IronCondor │ Buy    │   1 │   0.45 │          1 │       +96.00 │   +2,146.00 │
│ 2025-09-12 12:34:06 │ NVAX 19 Sep 2025 $7.5   │ Option          │ Put        │ Buy    │  50 │   0.14 │          0 │        +0.00 │   +2,146.00 │
│ 2025-09-15 14:19:28 │ LITE                    │ Stock           │ -          │ Buy    │  12 │ 170.87 │          0 │        +0.00 │   +2,146.00 │
│ 2025-09-15 14:20:20 │ ALAB                    │ Stock           │ -          │ Buy    │  10 │ 234.23 │          0 │        +0.00 │   +2,146.00 │
│ 2025-09-15 14:21:03 │ RMBS                    │ Stock           │ -          │ Buy    │  13 │  96.95 │          0 │        +0.00 │   +2,146.00 │
│ 2025-09-16 09:40:23 │ NVAX 19 Sep 2025 $7.5   │ Option          │ Put        │ Sell   │  50 │   0.02 │         50 │      -600.00 │   +1,546.00 │
│ 2025-09-17 13:37:00 │ SPXW 17 Sep 2025        │ Option Strategy │ Strategy   │ Sell   │   2 │   0.65 │          0 │        +0.00 │   +1,546.00 │
│ 2025-09-17 15:03:16 │ SPXW 17 Sep 2025        │ Option Strategy │ Strategy   │ Buy    │   2 │   0.15 │          2 │      +100.00 │   +1,646.00 │
│ 2025-09-17 15:40:24 │ SPXW 17 Sep 2025        │ Option Strategy │ Strategy   │ Sell   │   1 │   1.35 │          0 │        +0.00 │   +1,646.00 │
│ 2025-09-17 15:41:31 │ SPXW 17 Sep 2025        │ Option Strategy │ Strategy   │ Buy    │   1 │      1 │          1 │       +35.00 │   +1,681.00 │
│ 2025-09-18 10:27:23 │ SPXW 18 Sep 2025        │ Option Strategy │ Strategy   │ Buy    │  10 │   4.45 │          0 │        +0.00 │   +1,681.00 │
│ 2025-09-18 10:55:14 │ SPX 19 Sep 2025 $6640   │ Option          │ Put        │ Buy    │   1 │   16.7 │          0 │        +0.00 │   +1,681.00 │
│ 2025-09-18 10:58:04 │ SPX 19 Sep 2025 $6640   │ Option          │ Put        │ Sell   │   1 │   17.4 │          1 │       +70.00 │   +1,751.00 │
│ 2025-09-18 11:12:39 │ SPXW 18 Sep 2025        │ Option Strategy │ Strategy   │ Sell   │  10 │      4 │         10 │      -450.00 │   +1,301.00 │
│ 2025-09-19 14:59:54 │ SPXW 22 Sep 2025        │ Option Strategy │ IronCondor │ Sell   │   1 │   0.65 │          0 │        +0.00 │   +1,301.00 │
│ 2025-09-22 09:42:48 │ SPXW 22 Sep 2025        │ Option Strategy │ IronCondor │ Buy    │   1 │   0.15 │          1 │       +50.00 │   +1,351.00 │
│ 2025-09-22 12:14:35 │ SNDK 21 Nov 2025 $130   │ Option          │ Call       │ Buy    │   2 │    5.9 │          0 │        +0.00 │   +1,351.00 │
│ 2025-09-23 11:56:40 │ GOOG 16 Jan 2026 $275   │ Option          │ Call       │ Buy    │   5 │  11.55 │          0 │        +0.00 │   +1,351.00 │
│ 2025-10-03 11:59:12 │ ALAB                    │ Stock           │ -          │ Sell   │  10 │ 206.21 │         10 │      -280.20 │   +1,070.80 │
│ 2025-10-03 12:00:00 │ LITE                    │ Stock           │ -          │ Sell   │  12 │ 162.43 │         12 │      -101.28 │     +969.52 │
│ 2025-10-03 12:00:24 │ AMAT 19 Dec 2025 $240   │ Option          │ Call       │ Buy    │   3 │      9 │          0 │        +0.00 │     +969.52 │
│ 2025-10-06 12:01:36 │ GLW 19 Dec 2025 $110    │ Option          │ Call       │ Buy    │  30 │   0.91 │          0 │        +0.00 │     +969.52 │
│ 2025-10-06 14:08:40 │ GOOG 20 Feb 2026 $275   │ Option          │ Call       │ Buy    │  10 │  13.13 │          0 │        +0.00 │     +969.52 │
│ 2025-10-07 10:09:26 │ SNDK 21 Nov 2025 $130   │ Option          │ Call       │ Sell   │   2 │   14.2 │          2 │    +1,660.00 │   +2,629.52 │
│ 2025-10-07 10:32:58 │ STX 24 Oct 2025 $245    │ Option          │ Call       │ Buy    │   3 │    6.9 │          0 │        +0.00 │   +2,629.52 │
│ 2025-10-09 13:04:23 │ AMAT 19 Dec 2025 $240   │ Option          │ Call       │ Sell   │   3 │   9.25 │          3 │       +75.00 │   +2,704.52 │
│ 2025-10-21 09:34:53 │ STX 24 Oct 2025 $245    │ Option          │ Call       │ Sell   │   3 │   0.05 │          3 │    -2,055.00 │     +649.52 │
│ 2025-10-22 09:41:30 │ GOOG 20 Feb 2026 $275   │ Option          │ Call       │ Sell   │  10 │  15.91 │         10 │    +2,780.00 │   +3,429.52 │
│ 2025-10-22 09:44:04 │ GOOG 16 Jan 2026 $265   │ Option          │ Call       │ Buy    │   5 │   15.3 │          0 │        +0.00 │   +3,429.52 │
│ 2025-10-22 11:01:50 │ GOOG 16 Jan 2026 $275   │ Option          │ Call       │ Sell   │   5 │     12 │          5 │      +225.00 │   +3,654.52 │
│ 2025-10-24 12:42:23 │ OKLO 14 Nov 2025 $145   │ Option          │ Call       │ Buy    │   2 │  13.35 │          0 │        +0.00 │   +3,654.52 │
│ 2025-10-24 13:28:44 │ CRCL 28 Nov 2025 $150   │ Option          │ Call       │ Buy    │  10 │  14.85 │          0 │        +0.00 │   +3,654.52 │
│ 2025-10-24 13:32:14 │ CRCL 28 Nov 2025 $150   │ Option          │ Call       │ Sell   │  10 │  14.95 │         10 │      +100.00 │   +3,754.52 │
│ 2025-10-24 13:33:33 │ CRCL 19 Dec 2025 $200   │ Option          │ Call       │ Buy    │  10 │   9.55 │          0 │        +0.00 │   +3,754.52 │
│ 2025-10-27 12:01:50 │ MU 19 Dec 2025 $260     │ Option          │ Call       │ Buy    │   3 │   9.85 │          0 │        +0.00 │   +3,754.52 │
│ 2025-10-28 11:26:18 │ PYPL 21 Nov 2025 $85    │ Option          │ Call       │ Buy    │  10 │   1.02 │          0 │        +0.00 │   +3,754.52 │
│ 2025-10-29 10:19:15 │ OKLO 14 Nov 2025 $145   │ Option          │ Call       │ Sell   │   2 │     14 │          2 │      +130.00 │   +3,884.52 │
│ 2025-10-29 12:46:39 │ MU 19 Dec 2025 $260     │ Option          │ Call       │ Sell   │   3 │     14 │          3 │    +1,245.00 │   +5,129.52 │
│ 2025-10-31 11:40:02 │ MSFT 16 Jan 2026 $550   │ Option          │ Call       │ Buy    │   9 │   12.2 │          0 │        +0.00 │   +5,129.52 │
│ 2025-11-03 09:45:20 │ MSFT 16 Jan 2026 $550   │ Option          │ Call       │ Sell   │   9 │   12.8 │          9 │      +540.00 │   +5,669.52 │
│ 2025-11-03 09:50:04 │ MSFT 16 Jan 2026 $550   │ Option          │ Call       │ Buy    │  15 │  12.55 │          0 │        +0.00 │   +5,669.52 │
│ 2025-11-06 11:20:50 │ GOOG 16 Jan 2026 $265   │ Option          │ Call       │ Sell   │   5 │  29.85 │          5 │    +7,275.00 │  +12,944.52 │
│ 2025-11-06 12:14:43 │ GOOG 20 Mar 2026 $315   │ Option          │ Call       │ Buy    │   5 │  15.95 │          0 │        +0.00 │  +12,944.52 │


Open Positions
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━┳━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Instrument            ┃ Asset           ┃ Option     ┃ Side ┃ Qty ┃ Avg Price ┃      Expiry ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━╇━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ MSFT 16 Jan 2026 $550 │ Option          │ Call       │ Buy  │  15 │     12.55 │ 16 Jan 2026 │
│ GOOG 16 Jan 2026      │ Option Strategy │ IronCondor │ Sell │  20 │      0.75 │ 16 Jan 2026 │
│ BYDDY                 │ Stock           │ -          │ Buy  │   9 │    102.75 │           - │
│ RMBS                  │ Stock           │ -          │ Buy  │  13 │     96.95 │           - │
└───────────────────────┴─────────────────┴────────────┴──────┴─────┴───────────┴─────────────┘
Final realized P&L: -727.48
```

## Dev

```bash
uv sync
uv run webull-pnl --data-dir data
```
