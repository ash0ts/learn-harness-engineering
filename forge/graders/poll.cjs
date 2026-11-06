/** Await asynchronous IPC results in Node, never the truthiness of a Promise. */
async function poll(predicate, timeoutMs=10000) {
  const deadline=Date.now()+timeoutMs;
  do {
    if(await predicate())return;
    await new Promise(resolve=>setTimeout(resolve,50));
  } while(Date.now()<deadline);
  throw new Error('Timed out waiting for observed application state');
}
module.exports={poll};
