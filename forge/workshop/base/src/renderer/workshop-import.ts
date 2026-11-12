/** The surrounding typed bridge and dialog handler are supplied course code. */
export async function importFromPicker() {
  const file = await window.knowledgeBase.documents.choose();
  if (file) await window.knowledgeBase.documents.import(file);
}
