This PR adds a null check for document.body before referencing document.body.scrollHeight. The motivation is that in some cases (such as non-standard DOM structures or scripts running before the DOM is fully loaded), document.body can be null, which would previously have caused runtime errors.

The fix is appropriate and covers a genuine bug that may be encountered in edge cases. The solution is concise and maintains safety without introducing unnecessary complexity. Labeling the PR as bug and size:XS is accurate. No other unintended changes observed.

If not already done, consider adding a simple test or log to ensure scrollHeight is accessed only if document.body exists, even for future contributors. Otherwise, this looks good!

✅ LGTM! Thanks for improving the robustness of the codebase.
