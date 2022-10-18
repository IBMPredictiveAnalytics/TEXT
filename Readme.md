# TEXT
## Create a text block in the Viewer, optionally with formatted text 
 The command provides a way in syntax to create a block of text for comments and annotations of the output. The output can be plain text, html, or rtf.

---
Requirements
----
- IBM SPSS Statistics 18 or later and the corresponding IBM SPSS Statistics-Integration Plug-in for Python.

Note: For users with IBM SPSS Statistics version 23 or higher, the TEXT extension is installed as part of IBM SPSS Statistics-Essentials for Python.

---
Installation intructions
----
1. Open IBM SPSS Statistics
2. Navigate to Utilities -> Extension Bundles -> Download and Install Extension Bundles
3. Search for the name of the extension and click Ok. Your extension will be available.

---
Tutorial
----

### Installation Location

Utilities →

&nbsp;&nbsp;Create Text Output →

### UI
<img width="998" alt="image" src="https://user-images.githubusercontent.com/19230800/196513248-b20f4749-b616-441c-8530-6b272a20a97a.png">

### Syntax
Example:

> TEXT "Hello )USER on )CURDATE" <br />
> /OUTLINE HEADING="Comment" <br />
> TITLE="Comment".

### Output

<img width="536" alt="image" src="https://user-images.githubusercontent.com/19230800/196513593-c2591f4c-fb14-4f89-8898-7b2627b1d813.png">

---
License
----

- Apache 2.0
                              
Contributors
----

  - JKP, IBM SPSS
