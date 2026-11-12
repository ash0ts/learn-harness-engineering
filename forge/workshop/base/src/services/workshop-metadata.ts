export function documentMetadata(content:string) {
  return {
    wordCount: content.trim() ? content.trim().split(/\s+/).length : 0,
    lineCount: content.split(/\r?\n/).length,
    paragraphCount: content.split(/\n\s*\n/).filter(p=>p.trim()).length,
  };
}
