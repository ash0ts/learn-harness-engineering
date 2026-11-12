import type {DocumentService} from '../src/services/document-service';
import type {IndexingService} from '../src/services/indexing-service';
import type {QaService} from '../src/services/qa-service';
export interface Services {documents:DocumentService; index:IndexingService; qa:QaService}
export async function benchmark(services:Services, fixture:string, question:string) {
  const document=services.documents.importDocument(fixture);
  await services.index.startIndexing(document.id);
  const response=await services.qa.ask(question);
  return {documentId:document.id, chunkCount:services.index.getChunksForDocument(document.id).length,
    citationCount:response.citations.length, answer:response.answer};
}
