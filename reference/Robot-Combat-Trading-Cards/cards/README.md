# Cards Output

This folder is the default output target for generated card images.

## Generate cards for Bot Oblivion 2025
```bash
python Generate_Robot_Combat_Card_Deck.py --ttdb "cards/IRCL_TTDB.md" --event-name "Bot Oblivion 2025"
```

## Generate cards for another event in the TTDB
```bash
python Generate_Robot_Combat_Card_Deck.py --ttdb "cards/IRCL_TTDB.md" --event-name "Event Name"
```

The generator will create a subfolder per event (slugged name) and place
card PNGs there. PDFs are written to `output/<event-slug>/`.
