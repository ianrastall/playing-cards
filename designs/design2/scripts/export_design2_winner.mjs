/** Export the ImageGen silk winner to the six existing native formats.
 * ImageGen creates the art; this script registers and packages that saved art.
 * Requires Node and ImageMagick 7 on PATH. Does not modify the active catalog.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const version=process.argv[2]||'v2';
if(!['v1','v2'].includes(version))throw new Error('Choose v1 or v2');
const source=path.join(root,`sources/generated/design2-winner-${version}`);
const out=path.join(root,`build/design2-winner-${version}`);
const config=JSON.parse(fs.readFileSync(path.join(root,'deck.json'),'utf8'));
const colors=['prussian-blue','verdigris','madder-lake','manganese-violet','lamp-black'];
const formats=['poker','bridge','european-standard','jumbo','travel','tarot'];
const sw=1060,sh=1484,ground=[250,235,215],radius=3.5/25.4*300;
const digest=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const sourcePaths=colors.map(c=>path.join(source,c+'.png'));
const sourceHashes=sourcePaths.map(digest);
const masters=sourcePaths.map(p=>{
  const dims=execFileSync('magick',['identify','-format','%w %h',p]).toString();
  if(dims!==`${sw} ${sh}`)throw new Error(`Unexpected source dimensions: ${dims}`);
  return execFileSync('magick',[p,'-depth','8','rgb:-'],{maxBuffer:32e6});
});
const shared=masters[0];
fs.mkdirSync(out,{recursive:true});

function sample(a,x,y,c){
  x=Math.max(0,Math.min(sw-1,x));y=Math.max(0,Math.min(sh-1,y));
  const x0=Math.floor(x),y0=Math.floor(y),x1=Math.min(sw-1,x0+1),y1=Math.min(sh-1,y0+1),fx=x-x0,fy=y-y0;
  return (a[(y0*sw+x0)*3+c]*(1-fx)+a[(y0*sw+x1)*3+c]*fx)*(1-fy)+(a[(y1*sw+x0)*3+c]*(1-fx)+a[(y1*sw+x1)*3+c]*fx)*fy;
}
function piece(v,edges,values){
  for(let i=1;i<edges.length;i++)if(v<=edges[i])return values[i-1]+(v-edges[i-1])/(edges[i]-edges[i-1])*(values[i]-values[i-1]);
  return values.at(-1);
}
function coverage(x,y,w,h){
  if(x>=radius&&x<w-radius||y>=radius&&y<h-radius)return 255;
  let inside=0;
  for(let sy=0;sy<8;sy++)for(let sx=0;sx<8;sx++){
    const px=x+(sx+.5)/8,py=y+(sy+.5)/8;
    const dx=Math.max(radius-px,px-(w-radius),0),dy=Math.max(radius-py,py-(h-radius),0);
    if(dx*dx+dy*dy<=radius*radius)inside++;
  }
  return Math.round(inside/64*255);
}
function render(master,w,h){
  const a=Buffer.alloc(w*h*4),commonMask=Buffer.alloc(w*h),xs=new Float64Array(w);
  const bx=73*w/750,by=70*h/1050;
  const centerScale=(w-2*bx)/820;
  const cy=h/2-184*centerScale;
  for(let x=0;x<w;x++){
    const px=x+.5;
    xs[x]=piece(px,[0,23*w/750,bx,w/2,w-bx,w-23*w/750,w],[0,32,120,530,940,1028,1060])-.5;
  }
  for(let y=0;y<Math.ceil(h/2);y++){
    const sy=piece(y+.5,[0,16*h/1050,by,cy,h/2],[0,25,108,552,736])-.5;
    for(let x=0;x<w;x++){
      const sx=xs[x],i=(y*w+x)*4;
      let isCommon=sx>=120&&sx<=939&&sy>=108;
      if(version==='v2'){
        // Leave the colored wedges outside the rounded inner field with their border.
        const dx=Math.max(200-sx,sx-860,0),dy=Math.max(182-sy,0);
        isCommon=sx>=130&&sx<=930&&sy>=112&&dx*dx+dy*dy<=70*70;
      }
      commonMask[y*w+x]=Number(isCommon);
      const src=isCommon?shared:master;
      const rgb=[0,1,2].map(c=>sample(src,sx,sy,c));
      // Flatten warm near-white paper and ivory reserves while keeping ink edges.
      const strength=Math.min(1,Math.max(0,(rgb[0]-231)/12),Math.max(0,(rgb[1]-221)/13),Math.max(0,(rgb[2]-196)/14));
      for(let c=0;c<3;c++)a[i+c]=Math.round(rgb[c]*(1-strength)+ground[c]*strength);
      a[i+3]=coverage(x,y,w,h);
    }
  }
  if(h%2){
    const y=Math.floor(h/2);
    for(let x=0;x<Math.ceil(w/2);x++){
      const i=y*w+x,j=y*w+w-1-x;
      commonMask[i]=commonMask[j]=Math.min(commonMask[i],commonMask[j]);
    }
    for(let x=0;x<Math.ceil(w/2);x++)for(let c=0;c<4;c++){
      const i=(y*w+x)*4+c,j=(y*w+w-1-x)*4+c;
      a[i]=a[j]=Math.round((a[i]+a[j])/2);
    }
  }
  for(let y=Math.ceil(h/2);y<h;y++)for(let x=0;x<w;x++){
    const i=(y*w+x)*4,j=((h-1-y)*w+w-1-x)*4;
    a.copy(a,i,j,j+4);
    commonMask[y*w+x]=commonMask[(h-1-y)*w+w-1-x];
  }
  return {pixels:a,commonMask};
}
const records=[];
for(const fmt of formats){
  const [w,h]=config.formats[fmt].back_pixels;
  fs.mkdirSync(path.join(out,'backs',fmt),{recursive:true});
  let common=null;
  for(let ci=0;ci<colors.length;ci++){
    const color=colors[ci],{pixels:a,commonMask}=render(masters[ci],w,h);
    const rel=`backs/${fmt}/${color}.png`,dest=path.join(out,rel);
    execFileSync('magick',['-size',`${w}x${h}`,'-depth','8','rgba:-','-units','PixelsPerInch','-density','300','-define','png:color-type=6',dest],{input:a,maxBuffer:32e6});
    const saved=execFileSync('magick',[dest,'-depth','8','rgba:-'],{maxBuffer:32e6});
    if(!saved.equals(a))throw new Error(`Roundtrip mismatch: ${rel}`);
    let symmetric=true;
    for(let i=0;i<w*h;i++)for(let c=0;c<4;c++)if(a[i*4+c]!==a[(w*h-1-i)*4+c])symmetric=false;
    if(!symmetric)throw new Error(`Half-turn mismatch: ${rel}`);
    let sharedInterior=true;
    if(common){
      for(let i=0;i<w*h;i++)if(commonMask[i])for(let c=0;c<4;c++){
        if(a[i*4+c]!==common[i*4+c])sharedInterior=false;
      }
    }else common=a;
    if(!sharedInterior)throw new Error(`Interior mismatch: ${rel}`);
    records.push({id:`design2.back.${fmt}.${color}`,path:rel,format:fmt,color,pixels:[w,h],mode:'RGBA',ppi:300,trim_inches:config.formats[fmt].trim_inches,sha256:digest(dest),half_turn_exact:symmetric,shared_interior_exact:sharedInterior,lossless_roundtrip:true});
    console.log(`PASS ${fmt}/${color}`);
  }
}
for(let i=0;i<sourcePaths.length;i++)if(digest(sourcePaths[i])!==sourceHashes[i])throw new Error('Source changed');
const manifest={design:'Design 2',status:'provisional winner',version:Number(version.slice(1)),colors,formats,ground_rgb:ground,corner_radius_mm:3.5,source_center_pixel:[529.5,735.5],source_interior:'prussian-blue.png',format_fit:'Piecewise registration to Design 1 border proportions; central medallion uses equal horizontal/vertical scale; remaining height distributed through upper/lower pattern bands.',source_art_tool:'built-in image_gen',sources:sourcePaths.map((p,i)=>({path:path.relative(root,p).replaceAll('\\','/'),sha256:sourceHashes[i]})),cards:records};
fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
fs.copyFileSync(path.join(source,'prompts.json'),path.join(out,'prompts.json'));
const labels=c=>c.replaceAll('-',' ').replace(/\b\w/g,m=>m.toUpperCase());
const cards=()=>formats.map(f=>`<section><h2>${labels(f)}</h2><div class="cards">${colors.map(c=>`<figure><a href="backs/${f}/${c}.png"><img src="backs/${f}/${c}.png" alt="${labels(c)} ${labels(f)} silk back" loading="lazy"></a><figcaption>${labels(c)}</figcaption></figure>`).join('')}</div></section>`).join('\n');
fs.writeFileSync(path.join(out,'index.html'),`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Design 2 · Provisional winner</title><style>*{box-sizing:border-box}body{margin:36px;background:#eee6d9;color:#332b24;font:17px/1.5 Georgia,serif}h1,h2{font-weight:normal}h1{font-size:36px;margin-bottom:6px}.cards{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:22px}figure{margin:0}img{display:block;width:100%;height:auto}figcaption{padding:10px 0}section{margin-top:40px}a{color:inherit}small{font:14px system-ui}@media(max-width:900px){.cards{grid-template-columns:repeat(3,1fr)}}@media(max-width:550px){body{margin:18px}.cards{grid-template-columns:repeat(2,1fr)}}</style><h1>Design 2 · Provisional winner</h1><p>Silk ornament with five solid-color floral border grounds. Six formats, including Tarot.</p><p><small>30 native RGBA backs · 300 ppi · 3.5 mm corners · exact half-turn symmetry · shared interior across all colors</small></p>${cards()}<p><a href="manifest.json">Geometry and checks</a> · <a href="prompts.json">Image-generation prompts</a></p></html>`);
console.log(`Exported and checked ${records.length} provisional backs in ${out}`);
