## 002 - doc type tag proposal
### Status
accepted
### Context
standard type tag for payload data originally planned for strings naturally 
becomes doc type through format differentiation.
### Decision
Fifth considers a doc type for all data to be rendered in the
1111 tag. The 28bit payload is logically split in four 7bit units parsed according to the first unit ( bits 27-21 ):

| value  | type  | category |
|--------|-------|---|
| 32-127 | ASCII |Printable ASCII character|
| 2-31   | len | Number of elements of the doc   |
| 1      | meta | Metadata in the following three 7bit units. Meta options pending.|
| 0      | unicode | 21bit codepoint in the remainint 7bit units. Can be non printable.|

### Consequence
Dropping the string as a primitive datatype in favor of the richer doc type
allows easy processing of richer data. Following the fractal approach, this allows arbitrary length "readable" data to
be processed in a formatted way, numerical data as well as variables
can be seamlessly integrated into text bodies without complicated
parsing syntax. The constraint is, that an element has a maximum size of 31
sub-elements, which is uncritical, since the sub-elements can likewise be 
subdivided. A doc in its simplest form could be an ASCII string of length 123
(30 cells x 4 characters + 3 in the first cell) an HTML page or a complex report
containing macros and spreadsheets. 