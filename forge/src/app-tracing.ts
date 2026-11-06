/** Serialize SDK initialization and flush only after the final app session closes. */
export class AppTracingLifecycle {
  private gate:Promise<unknown>=Promise.resolve();
  private key?:string;
  private references=0;
  constructor(private initialize:()=>Promise<void>,private shutdown:()=>Promise<void>) {}
  private serialize<T>(work:()=>Promise<T>):Promise<T> {
    const result=this.gate.then(work,work);this.gate=result.catch(()=>{});return result;
  }
  async retain(key:string) {
    await this.serialize(async()=>{
      if(this.key!==undefined&&this.key!==key)throw new Error('Concurrent app tracing must use the same project and credentials');
      if(this.references===0){await this.initialize();this.key=key;}
      this.references++;
    });
    let released=false;
    return ()=>this.serialize(async()=>{
      if(released)return;released=true;
      if(--this.references===0)try{await this.shutdown();}finally{this.key=undefined;}
    });
  }
}
