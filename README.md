Based on my work of [MK11-Api](https://github.com/thethiny/Mortal-Kombat-11-Tools/tree/master/mk11-api/mk11-mitm-server)

## x-ag-binary format

| Data Type             | Binary Format | Data Size               |
| --------------------- | ------------- | ----------------------- |
| ZERO                  | 00            | 1 byte                  |
| NULL                  | 01            | 1 byte                  |
| TRYE                  | 02            | 1 byte                  |
| FALSE                 | 03            | 1 byte                  |
| SINT8                 | 10            | 1 byte                  |
| UINT8                 | 11            | 1 byte                  |
| SINT16                | 12            | 2 bytes                 |
| UINT16                | 13            | 2 bytes                 |
| SINT32                | 14            | 4 bytes                 |
| UINT32                | 15            | 4 bytes                 |
| SINT64                | 16            | 8 bytes                 |
| UINT64                | 17            | 8 bytes                 |
| FLOAT                 | 20            | 4 bytes                 |
| FLOAT                 | 21            | 8? bytes                |
| CHAR8                 | 30            | 1 byte length + string  |
| CHAR16                | 31            | 2 bytes length + string |
| CHAR32                | 32            | 4 bytes length + string |
| BYTES8                | 33            | 1 byte length + data    |
| BYTES16               | 34            | 2 bytes length + data   |
| BYTES32               | 35            | 4 bytes length + data   |
| BIG INT size 8        | 36            | 8 bytes                 |
| EPOCH TIME            | 40            | 8 bytes                 |
| ARRAY8  `[`           | 50            | 1 byte items count      |
| ARRAY16 `[`           | 51            | 2 bytes items count     |
| ARRAY32 `[`           | 52            | 4 bytes items count     |
| ARRAY64 `[`           | 53            | 8 bytes items count     |
| MAP8  `{`             | 60            | 1 byte items count      |
| MAP16 `{`             | 61            | 2 bytes items count     |
| MAP32 `{`             | 62            | 4 bytes items count     |
| MAP64 `{`             | 63            | 8 bytes items count     |
| UMAP1 `{`             | 68            | 1 ubyte items count     |
| UMAP2 `{`             | 69            | 2 ubyte items count     |
