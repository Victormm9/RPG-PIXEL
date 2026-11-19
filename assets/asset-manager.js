(function () {
 "use strict";
 class AssetManager {
  constructor(manifest){
   this.manifest=manifest;
   this.images=new Map();
   this.failed=new Map();
   this.ready=this.loadAll();
  }
  async loadAll(){
   await Promise.all(Object.entries(this.manifest).map(async([key,asset])=>{
    try{
     if(!asset.available){
      throw new Error("PNG ainda não adicionado; confira o caminho e a especificação.");
     }
     const image=new Image();
     image.src=asset.path;
     await image.decode();
     if(image.naturalWidth!==asset.width||image.naturalHeight!==asset.height){
      throw new Error(`Esperado ${asset.width}x${asset.height}px; recebido ${image.naturalWidth}x${image.naturalHeight}px.`);
     }
     this.images.set(key,image);
    }catch(error){
     this.failed.set(key,{path:asset.path,spec:asset.spec,error:error.message});
    }
   }));
   return this;
  }
  image(key){return this.images.get(key)||null}
  frame(key,row,column,frameWidth,frameHeight){
   const image=this.image(key),asset=this.manifest[key];
   if(!image||!asset)return null;
   const columns=asset.width/frameWidth,rows=asset.height/frameHeight;
   if(!Number.isInteger(columns)||!Number.isInteger(rows)||column<0||column>=columns||row<0||row>=rows){
    return null;
   }
   return{x:column*frameWidth,y:row*frameHeight,width:frameWidth,height:frameHeight,image};
  }
  drawFrame(ctx,key,row,column,frameWidth,frameHeight,x,y,width=frameWidth,height=frameHeight){
   const image=this.image(key),asset=this.manifest[key];
   if(!image||!asset)return false;
   const columns=asset.width/frameWidth,rows=asset.height/frameHeight;
   if(!Number.isInteger(columns)||!Number.isInteger(rows)||column<0||column>=columns||row<0||row>=rows)return false;
   ctx.drawImage(image,column*frameWidth,row*frameHeight,frameWidth,frameHeight,x,y,width,height);
   return true;
  }
  missing(){return Array.from(this.failed.values())}
 }
 window.DrakmorAssetManager=AssetManager;
})();
