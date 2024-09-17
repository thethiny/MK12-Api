Based on my work of [MK11-Api](https://github.com/thethiny/Mortal-Kombat-11-Tools/tree/master/mk11-api/mk11-mitm-server)

## x-ag-binary format

| Data Type             | Binary Format | Data Size               |
| --------------------- | ------------- | ----------------------- |
| zero                  | 00            | 1 byte                  |
| null                  | 01            | 1 byte                  |
| true                  | 02            | 1 byte                  |
| false                 | 03            | 1 byte                  |
| sint8                 | 10            | 1 byte                  |
| uint8                 | 11            | 1 byte                  |
| sint16                | 12            | 2 bytes                 |
| uint16                | 13            | 2 bytes                 |
| sint32                | 14            | 4 bytes                 |
| uint32                | 15            | 4 bytes                 |
| sint64                | 16            | 8 bytes                 |
| uint64                | 17            | 8 bytes                 |
| FLOAT                 | 20            | 4 bytes                 |
| FLOAT                 | 21            | 8? bytes                |
| CHAR8                 | 30            | 1 byte length + string  |
| CHAR16                | 31            | 2 bytes length + string |
| CHAR32                | 32            | 4 bytes length + string |
| BYTES8                | 33            | 1 byte length + data    |
| BYTES16               | 34            | 2 bytes length + data   |
| BYTES32               | 35            | 4 bytes length + data   |
| long long int, size 8 | 36            | 8 bytes                 |
| epoch time            | 40            | 8 bytes                 |
| Array8 `[`            | 50            | 1 byte items count      |
| Array16 `[`           | 51            | 2 bytes items count     |
| Array32 `[`           | 52            | 4 bytes items count     |
| Array64 `[`           | 53            | 8 bytes items count     |
| MAP8 `{`              | 60            | 1 byte items count      |
| MAP16 `{`             | 61            | 2 bytes items count     |
| MAP32 `{`             | 62            | 4 bytes items count     |
| MAP64 `{`             | 63            | 8 bytes items count     |
| UMAP1 `{`             | 68            | 1 ubyte items count     |
| UMAP2 `{`             | 69            | 2 ubyte items count     |
