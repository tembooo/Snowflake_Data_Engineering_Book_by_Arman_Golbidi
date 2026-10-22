# Building and Editing the Book

The archive includes the entire 15-chapter book (the text is not regenerated in this build). All page design and numbering are taken from the individual source PDFs.

## Read the existing book

Open [Snowflake_Data_Engineering_Arman Golbidi.pdf](Snowflake_Data_Engineering_Arman%20Golbidi.pdf): 282 physical PDF pages, consisting of front cover, 280 chapter pages, and back cover.

## Build the print master

Install XeLaTeX and the packages `geometry`, `pdfpages` and `hyperref`. From the repository root:

```shell
xelatex -interaction=nonstopmode -halt-on-error Snowflake_Data_Engineering_PRINT_MASTER.tex
xelatex -interaction=nonstopmode -halt-on-error Snowflake_Data_Engineering_PRINT_MASTER.tex
```

`Snowflake_Data_Engineering_PRINT_MASTER.tex` is the original top-level print master. It embeds `covers/front.pdf`, the complete ordered set of `chapters/chapter_01.pdf` through `chapters/chapter_15.pdf`, then `covers/back.pdf`. Those support files have now been added from the exact included source PDFs and the cover pages of the supplied compiled book.

## Edit a chapter safely

1. Select the chapter's independently compilable `.tex` source (for example `Chapter_15/Snowflake_Data_Engineering_Chapter_15.tex`).
2. Compile that source with XeLaTeX in its own directory. Check that chapter's expected page range and formatting. Do not substitute a changed source file for a compiled PDF without compiling and testing it.
3. Replace the matching file under `chapters/chapter_XX.pdf` with the newly verified PDF.
4. Rebuild the print master and check page numbering and visual layout.
5. Retain the original file and a version-control history of each editorial change.

The original all-book PDF and chapter PDFs remain included for comparison. These are pre-typeset pages, not a continuous cross-chapter LaTeX typesetting pass; changes in chapter pagination must be reconciled before a print run.

## Verification

- Confirm the PDF is 178 x 254 mm, with a one-page front cover and one-page back cover.
- Confirm each chapter starts with the intended page number (first chapter: printed page 009; last chapter: 265).
- Confirm total chapter page count remains 280; currently per-chapter physical page counts are: 12, 18, 18, 20, 20, 16, 20, 18, 20, 20, 18, 18, 22, 16, 24.
- Confirm no missing images, tables or code listings.
- Treat original text and source attribution as separate review tasks. Do not infer cloud execution or commercial reuse rights from local compilation.
