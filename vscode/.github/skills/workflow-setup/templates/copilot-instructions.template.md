# Workspace guide

<!-- setup:brief -->
{{brief}}
<!-- /setup:brief -->

## Repositories

<!-- setup:repositories -->
{{repositories}}
<!-- /setup:repositories -->

## Task routes

<!-- setup:routes -->
{{routes}}
<!-- /setup:routes -->

## Checks

<!-- setup:checks -->
{{checks}}
<!-- /setup:checks -->

## Workspace documents

<!-- setup:documents -->
{{documents}}
<!-- /setup:documents -->

## Team rules

<!-- setup:team -->
{{team}}
<!-- /setup:team -->

Work on the user's current checkout. Never switch branches or revisions or create a branch, including through subagents, unless the user asks for it.

## Team additions

<!-- Setup rewrites only the marked parts above and keeps this section. Add one-line team rules here. -->
- Question tool: keep each question within 40 words and its options short. Put the background in chat before calling the tool, because the tool crops long text.
- Package sync: run `/workflow-setup` and ask it to sync the package from ai-core-workflow. Each sync clones the latest `main` into a temporary folder and deletes it afterwards. List each local override of a package file here as `- Override .github/<file>: <reason>.`
