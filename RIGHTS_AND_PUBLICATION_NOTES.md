# Rights, Privacy, and Publication-Readiness Notes

This repository is an author-provided educational manuscript archive. It is not a commercially validated or licensed retail release.

## Before making the repository public

- Review personal photographs and design/promotional drafts stored under `Chapter_11/prompt4-jelde ketab/`. Ensure the author has permission to publish every depicted person and asset.
- Check the front and back covers in `Images/`; the back image includes a printed ISBN/barcode. The image's displayed digits have **not been verified as a formally assigned ISBN** and should not be used on sale listings or submitted as an official identifier without replacement/approval. The digits shown in the uploaded cover also do not appear to satisfy the ISBN-13 check-digit calculation.
- Audit all source files for secrets, access tokens, service-account credentials, private datasets and sensitive personal information before publication. Template examples are not proof of absence of secrets.
- Set explicit copyright and code-licensing terms by adding a `LICENSE` if public reuse is intended. No license was supplied for the book/labs in the input archive.
- Review any included marketing artwork for third-party logos, trademarks, rights of publicity and commercial-use restrictions.
- A linked GitHub repository has its **own license**. A reference index does not grant permission to republish its code, screenshots or text.
- An AI-free authorship statement is not supported by the documented creation process. The README uses a factual editorial disclosure instead.

## Before a technical release

- Review all Snowflake SQL and Python examples against the targeted current account region, edition and dependency versions.
- Run selected labs end-to-end in a disposable Snowflake environment, retaining results, query IDs and cleanup proof.
- Confirm Power BI exports/semantic models and cloud connections in real supported software; illustrative M/DAX files are not a functioning `.pbix` report.
- Independently review data provenance, AI/Cortex cost claims, RBAC policies and production threat models.
- Verify printed pagination, front matter, appendices, references, ISBN and bibliographic metadata with a publisher or publishing service.

## Included vs. externally linked work

The 15 chapter labs are included as local source files. The 181 numbered GitHub repositories in the README are external literature/tutorial/reference pointers; their code is *not* included simply by virtue of appearing in the source directory.
