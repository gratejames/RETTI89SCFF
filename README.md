# Reverse engineering the TI89 StudyCards file format
James Smythe, September 2, 2024

With much thanks to Romain Liévin and Tim Singer for their work on documenting the variable file format, which can be found at their site: https://merthsoft.com/linkguide/ti89/fformat.html

![Color coded binary file](https://raw.githubusercontent.com/gratejames/RETTI89SCFF/main/RETTI89SCFF.png)

The full format is a nested mess of containers, but I hope to explain it first by repeating the relevant information from existing documentation on the variable file format itself, then moving on to list each layer at a time. For a basic outline, each file contains a single stack, which contains a list of cards. Each card has a front and a back, which each have lines of text. All numbers are in little-endian, least significant bytes first. Except for one, of course!

Oh, and many of the things labeled 'signature' are just constants that don't change while fiddling with the official card editor. Many could adjust hidden settings, while others might actually just be signatures. More investigation is warranted, especially considering images and other stack types. The investigation here only pertains to the “Self-Check” stacks, but none of the other three.

## The variable file
This is where the journey begins: the file itself. Again, nearly all of this first section is taken directly from the wonderful work documented on merthsoft.com, and is common between all single-variable files (Except the Type ID).

| Offset | Length   | Description                                                |
| ------ | -------- | ---------------------------------------------------------- |
| 0x00   | 8 bytes  | Signature: "\*\*TI89\*\*"                                  |
| 0x08   | 2 bytes  | Signature: 0x01, 0x00                                      |
| 0x0a   | 8 bytes  | Folder: "main"*                                            |
| 0x12   | 40 bytes | Comment: "AppVariable file MM/DD/YY, HH:MM"*               |
| 0x3a   | 2 bytes  | Number of variables: 0x01                                  |
| 0x3c   | 4 bytes  | Offset from file start to beginning of variable data: 0x52 |
| 0x40   | 8 bytes  | Variable name*                                             |
| 0x48   | 1 byte   | Type id: 0x1c                                              |
| 0x49   | 3 bytes  | Always zero (Attributes and unused)                        |
| 0x4c   | 4 bytes  | File size, in bytes                                        |
| 0x50   | 2 bytes  | Signature: 0xa5, 0x5a                                      |
| 0x52   | n bytes  | Variable data / stack data                                 |
| 0x52+n | 2 bytes  | Checksum: sum of all bytes in variable data                |

*Padded with 0 to fill size

## The variable data
| Offset  | Length   | Description                                           |
| ------- | -------- | ----------------------------------------------------- |
| 0x00    | 4 bytes  | Prefix: all 0                                         |
| 0x04    | 2 bytes  | Length of variable data **IN BIG ENDIAN**             |
| 0x06    | 4 bytes  | Signature: 0xf3 0x47 0xbf 0xa7                        |
| 0x0a    | 4 bytes  | *Unknown*: 1, 0, 0, 0                                 |
| 0x0e    | 2 bytes  | Offset* of title                                      |
| 0x10    | 2 bytes  | Offset* of creator                                    |
| 0x12    | 2 bytes  | Offset* of Date                                       |
| 0x14    | 2 bytes  | Offset* of Version                                    |
| 0x16    | 3 bytes  | Points for right(+), wrong(-), and skipped(-) answers |
| 0x19    | 1 bytes  | Amount of cards: n                                    |
| 0x1a    | 2n bytes | Card pointer table: 2 bytes offsets* to card titles   |
| 0x1a+2n | -        | Metadata                                              |
| -       | -        | Cards                                                 |
| -       | 4 bytes  | Signature: "STDY"                                     |
| -       | 2 bytes  | Signature: 0x00 0xf8                                  |

*Starts from beginning of signature at 0x06

## The stack metadata

Metadata fields are zero-terminated and are not validated

| Description     |
| --------------- |
| Signature: 0x02 |
| Stack title     |
| Creator name    |
| Creation date   |
| Version number  |

## The card entry format
Now for the exciting part: the cards format!

| Offset | Length | Description                        |
| ------ | ------ | ---------------------------------- |
| 0x00   | 2      | Pointer to beginning of card front |
| 0x02   | 2      | Pointer to beginning of card back  |
| 0x04   | -      | Card title, zero terminated        |
| -      | -      | Card face: front                   |
| -      | -      | *Unknown*: 0x01                    |
| -      | -      | Card face: back                    |

## The card face
| Offset | Length  | Description                                                         |
| ------ | ------- | ------------------------------------------------------------------- |
| 0x00   | 3 bytes | *Unknown*: 0x01 0x03 0x00                                           |
| 0x03   | 1 bytes | Amount of lines on card face                                        |
| 0x04   | n bytes | Text entries: 0x01, y position, x position, contents (0 terminated) |
| 0x04+n | 3 bytes | *Unknown*: 0x50 0x01 0x01                                           |

