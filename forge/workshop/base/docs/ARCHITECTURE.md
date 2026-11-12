# Architecture
src/main/ipc-handlers.ts owns native dialogs and document content. src/preload/preload.ts exposes typed calls. src/renderer/components/DocumentDetail.tsx displays content. Keep credentials in main/service code. Verify persistence with npm test and the restart UI scenario.
