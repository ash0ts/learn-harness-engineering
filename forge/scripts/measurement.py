"""Read-only acceptance qualifications; original trial grades remain immutable."""

HISTORY_SELECTOR_SOURCE = 'b948c1fbac36bca7dae458795d9bfca3f5d2b7d3'
HISTORY_SELECTOR_NOTE = (
    'Project 05 at source b948c1fbac36 used an overly broad citation selector: '
    'it clicked answer prose containing "citations" instead of an expand control. '
    'Its native grades remain archived but are excluded from qualified comparisons. '
    'The corrected checker selects interactive citation controls and exercises '
    'both cancellation and acceptance of native or custom confirmation dialogs. '
    'All three role treatments are rerun from the same unfinished code and model settings. '
    'Project 06 at that source also omitted the feedback.submit argument contract while '
    'its checker assumed positional arguments. The corrected task specifies an object '
    'with question, answer, rating and optional comment; both capstone treatments are rerun.'
)

def qualified(row):
    revision = row.get('protocolRevision', row.get('protocol', {}).get('protocolRevision', 1))
    return revision >= 4 and not (
        row['project'] in ['project-05', 'project-06'] and row['sourceCommit'] == HISTORY_SELECTOR_SOURCE
    )

def reason(row):
    revision = row.get('protocolRevision', row.get('protocol', {}).get('protocolRevision', 1))
    if revision < 4:
        return 'Historical asynchronous UI waits do not establish visible-answer acceptance.'
    if not qualified(row):
        return HISTORY_SELECTOR_NOTE
    return 'Protected service checks and awaited visible-answer Electron acceptance.'
