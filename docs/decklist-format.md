# Decklist Format Guide

This guide explains how to write decklist files for the Decklist to PDF tool.

## 📄 Basic Format

Each line in a decklist represents cards to print:

```
COPIES CARD_NAME (SET) COLLECTOR_NUMBER
```

### Example

```
4 Lightning Bolt (2X2) 117
2 Counterspell (CMM) 81
1 Sol Ring (CMM) 421
```

## 📋 Finding Card Information

### From Scryfall

1. Go to [scryfall.com](https://scryfall.com)
2. Search for your card
3. Look at the URL: `scryfall.com/card/SET/NUMBER/card-name`
4. Use SET and NUMBER in your decklist

**Example:**
- URL: `scryfall.com/card/cmm/81/counterspell`
- Decklist: `1 Counterspell (CMM) 81`

### Set Codes

Set codes are 3-4 character identifiers. Common examples:

| Set Code | Set Name |
|----------|----------|
| `2X2` | Double Masters 2022 |
| `CMM` | Commander Masters |
| `MH3` | Modern Horizons 3 |
| `DMU` | Dominaria United |
| `ONE` | Phyrexia: All Will Be One |
| `VMA` | Vintage Masters |
| `ICE` | Ice Age |

## 💬 Comments

Lines starting with `#` are ignored:

```
# Main Deck
4 Lightning Bolt (2X2) 117
2 Counterspell (CMM) 81

# Sideboard
# 2 Negate (CMM) 98
```

Empty lines are also ignored.

## 🔄 Two-Sided Cards

### Transform/Modal DFC Cards

For double-faced cards, use the standard format. The script detects two-sided cards automatically:

```
1 Delver of Secrets (MID) 47
```

### Force Front Side Only

Prefix with `!` to print only the front face:

```
!1 Delver of Secrets (MID) 47
```

### Force Back Side Only

Prefix with `!!` to print only the back face:

```
!!1 Delver of Secrets (MID) 47
```

## 🎨 Custom Cards

For custom or proxy cards, prefix the name with `*`:

```
1 *My Custom Card
```

Requirements:
- Place the image as `custom_cards/My Custom Card.png`
- Image should be 745×1040 pixels for best quality
- PNG format recommended

## 🔀 Composite Cards

Create cards with custom front/back combinations using `||`:

```
1 Lightning Bolt (2X2) 117 || Counterspell (CMM) 81
```

This prints:
- Front: Lightning Bolt
- Back: Counterspell

### Custom Front or Back

Mix Scryfall cards with custom images:

```
1 Lightning Bolt (2X2) 117 || *MyCustomBack
1 *MyCustomFront || Counterspell (CMM) 81
```

## 📝 Complete Example

```
# ============================================
# Mono-Red Burn - Modern
# ============================================

# Creatures
4 Goblin Guide (ZEN) 126
4 Monastery Swiftspear (BRO) 144
4 Eidolon of the Great Revel (JOU) 94

# Instants
4 Lightning Bolt (2X2) 117
4 Lava Spike (MMA) 121
4 Rift Bolt (TSR) 184
4 Searing Blaze (WWK) 90
4 Skullcrack (GTC) 106

# Sorceries
4 Light Up the Stage (RNA) 107

# Lands
4 Inspiring Vantage (KLD) 246
4 Sacred Foundry (GRN) 254
4 Sunbaked Canyon (MH1) 247
2 Fiery Islet (MH1) 238
2 Mountain (UNF) 235

# ============================================
# Sideboard
# ============================================
3 Smash to Smithereens (ORI) 163
3 Roiling Vortex (ZNR) 156
2 Exquisite Firecraft (ORI) 143
2 Path to Exile (2XM) 25
2 Deflecting Palm (KTK) 173
3 Kor Firewalker (WWK) 11

# ============================================
# Custom Tokens
# ============================================
# 4 *Goblin Token
```

## ⚠️ Format Rules

### Do's ✅

- Use exact card names as shown on Scryfall
- Include spaces in card names: `Monastery Swiftspear` not `MonasterySwiftspear`
- Use uppercase set codes: `(CMM)` not `(cmm)` (though lowercase works)
- Start each line with a number

### Don'ts ❌

- Don't include special characters not in the card name
- Don't use alternate card names
- Don't add extra spaces around parentheses

### Valid Lines

```
4 Lightning Bolt (2X2) 117        ✅
1 Sol Ring (CMM) 421              ✅
!1 Delver of Secrets (MID) 47     ✅
1 *Custom Card                    ✅
1 Card (SET) 123 || Other (SET) 1 ✅
```

### Invalid Lines

```
Lightning Bolt (2X2) 117          ❌ Missing count
4 Lightning Bolt 117              ❌ Missing set
4 Lightning Bolt (2X2)            ❌ Missing number
4                                 ❌ Missing card info
```

## 🔍 Troubleshooting

### "Card not found in card data"

1. Verify the set code is correct on Scryfall
2. Check the collector number matches
3. Update Scryfall bulk data if the card is new
4. Check for typos in the card name

### "Invalid decklist line"

1. Ensure the line starts with a number
2. Check for missing parentheses around set code
3. Verify there's a space between all elements

### Custom Card Not Found

1. Ensure file exists at `custom_cards/NAME.png`
2. Name must match exactly (case-sensitive on Linux/macOS)
3. Use `.png` extension

---

[← Configuration](configuration.md) | [Back to Home](README.md)
