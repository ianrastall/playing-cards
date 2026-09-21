/** Build reusable face components from the saved ImageGen master.
 * node designs/design2/scripts/build_face_frames.mjs
 * ImageMagick handles sampling/PNG encoding; no generation calls at build time.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const revision='design2-face-frames-v1';
const dest=path.join(root,'sources/components',revision);
const source=path.join(root,'sources/generated',revision,'frame-master.png');
const config=JSON.parse(fs.readFileSync(path.join(root,'deck.json'),'utf8'));
const ground=[250,235,215];
const palettes={'lamp-black':[33,33,31],'madder-lake':[167,52,67]};
const W=750,H=1050;
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const relative=p=>path.relative(root,p).replaceAll('\\','/');
function magick(args,input){return execFileSync('magick',args,{input,maxBuffer:64e6});}
function save(a,w,h,file,ch=4){
  fs.mkdirSync(path.dirname(file),{recursive:true});
  magick(['-size',`${w}x${h}`,'-depth','8',ch===4?'rgba:-':'gray:-','-units','PixelsPerInch','-density','300','-define','png:exclude-chunks=tEXt,zTXt,iTXt,tIME','-define',`png:color-type=${ch===4?6:0}`,file],a);
  return {path:relative(file),sha256:hash(file)};
}
function resize(a,w,h,nw,nh,ch){
  if(w===nw&&h===nh)return Buffer.from(a);
  return magick(['-size',`${w}x${h}`,'-depth','8',ch===4?'rgba:-':'gray:-','-filter','Lanczos','-resize',`${nw}x${nh}!`,'-depth','8',ch===4?'rgba:-':'gray:-'],a);
}
function reciprocal(a,w,h,ch,blend=0){
  const original=Buffer.from(a);
  for(let y=0;y<Math.ceil(h/2);y++)for(let x=0;x<w;x++)for(let c=0;c<ch;c++){
    const i=(y*w+x)*ch+c,j=((h-1-y)*w+w-1-x)*ch+c;
    // Fade into an average at the center, avoiding a hard splice in the vines.
    const t=blend?Math.max(0,1-Math.abs(y-(h-1)/2)/blend)*.5:0;
    const value=Math.round(original[i]*(1-t)+original[j]*t);
    if(i===j)a[i]=value;
    else if(y<(h-1)/2){a[i]=value;a[j]=value;}
    else if(x<=w-1-x){a[i]=a[j]=Math.round((original[i]+original[j])/2);}
  }
  return a;
}
function flood(rgb,w,h,x,y){
  const allowed=i=>rgb[i*4]>225&&rgb[i*4+1]>210&&rgb[i*4+2]>185;
  const mask=Buffer.alloc(w*h),queue=new Int32Array(w*h);let first=0,last=0;
  const start=y*w+x;if(!allowed(start))throw Error('Seed outside pale region');
  queue[last++]=start;mask[start]=255;
  while(first<last){
    const i=queue[first++],xx=i%w;
    for(const n of [xx?i-1:-1,xx<w-1?i+1:-1,i>=w?i-w:-1,i<w*(h-1)?i+w:-1]){
      if(n>=0&&!mask[n]&&allowed(n)){mask[n]=255;queue[last++]=n;}
    }
  }
  return mask;
}
function silhouette(w,h){
  const mask=Buffer.alloc(w*h),r=3.5/25.4*300;
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){
    let n=0;
    for(let sy=0;sy<8;sy++)for(let sx=0;sx<8;sx++){
      const px=x+(sx+.5)/8,py=y+(sy+.5)/8;
      const dx=Math.max(r-px,px-(w-r),0),dy=Math.max(r-py,py-(h-r),0);
      if(dx*dx+dy*dy<=r*r)n++;
    }
    mask[y*w+x]=Math.round(n/64*255);
  }
  return mask;
}
function box(mask,w,h,topOnly=false){
  let l=w,t=h,r=0,b=0;
  for(let y=0;y<(topOnly?Math.floor(h/2):h);y++)for(let x=0;x<w;x++)if(mask[y*w+x]>128){l=Math.min(l,x);t=Math.min(t,y);r=Math.max(r,x);b=Math.max(b,y);}
  return [l,t,r+1,b+1];
}
let plate=magick([source,'-alpha','on','-filter','Lanczos','-resize',`${W}x${H}!`,'-depth','8','rgba:-']);
reciprocal(plate,W,H,4,12);
const field=flood(plate,W,H,375,525),panel=flood(plate,W,H,70,145),outside=flood(plate,W,H,375,4);
for(let i=0;i<W*H;i++)panel[i]=Math.max(panel[i],panel[W*H-1-i]);
const paletteMask=Buffer.alloc(W*H);
for(let i=0;i<W*H;i++){
  const x=i%W,y=Math.floor(i/W);
  // Remove the generated hairline at the trim edge without touching frame ink.
  const paper=field[i]||panel[i]||outside[i]||x<12||x>=W-12||y<10||y>=H-10;
  if(paper){for(let c=0;c<3;c++)plate[i*4+c]=ground[c];}
  else{
    const [r,g,b]=plate.subarray(i*4,i*4+3),hi=Math.max(r,g,b),lo=Math.min(r,g,b);
    // Neutral dark ink is the only variable color; gold remains shared.
    const weight=Math.min(1,Math.max(0,(125-hi)/70))*Math.min(1,Math.max(0,(42-(hi-lo))/28));
    paletteMask[i]=Math.round(weight*255);
  }
}
reciprocal(plate,W,H,4);reciprocal(field,W,H,1);reciprocal(panel,W,H,1);reciprocal(paletteMask,W,H,1);
const manifest={revision,status:'frame-components',source:{path:relative(source),sha256:hash(source),tool:'built-in image_gen',prompts:'sources/generated/'+revision+'/prompts.json'},ground_rgb:ground,palettes,corner_radius_mm:3.5,ppi:300,
  construction:'Shared generated Poker master and masks, format-aware component resampling as in Design 1; European Standard derives from Bridge. Exact half-turn registration and physical corner alpha are reapplied after sampling. Border ornament scales with the canvas; these are not independent native-format generations.',
  face_palette_policy:{spades:'lamp-black',clubs:'lamp-black',hearts:'madder-lake',diamonds:'madder-lake','black-joker':'lamp-black','red-joker':'madder-lake'},formats:{}};
const prepared={};
for(const fmt of ['poker','bridge','european-standard','jumbo','travel','tarot']){
  const [w,h]=config.formats[fmt].back_pixels;
  const src=fmt==='european-standard'?prepared.bridge:{plate,field,panel,paletteMask,w:W,h:H};
  const parts={w,h};
  for(const [key,ch] of [['plate',4],['field',1],['panel',1],['paletteMask',1]])parts[key]=reciprocal(resize(src[key],src.w,src.h,w,h,ch),w,h,ch);
  const alpha=silhouette(w,h);
  for(let i=0;i<w*h;i++){
    parts.plate[i*4+3]=alpha[i];
    // Fully blank saved aperture/cartouches, including resampled interiors.
    if(parts.field[i]===255||parts.panel[i]===255)for(let c=0;c<3;c++)parts.plate[i*4+c]=ground[c];
    if(parts.field[i]||parts.panel[i])parts.paletteMask[i]=0;
  }
  prepared[fmt]=parts;
  const dir=path.join(dest,fmt),files={};
  files.field=save(parts.field,w,h,path.join(dir,'field-mask.png'),1);
  files.panels=save(parts.panel,w,h,path.join(dir,'panel-mask.png'),1);
  files.palette=save(parts.paletteMask,w,h,path.join(dir,'frame-color-mask.png'),1);
  files.outline=save(alpha,w,h,path.join(dir,'outline-mask.png'),1);
  const frames={};
  for(const [color,rgb] of Object.entries(palettes)){
    const output=Buffer.from(parts.plate);
    for(let i=0;i<w*h;i++)for(let c=0;c<3;c++){
      const mix=parts.paletteMask[i]/255;
      output[i*4+c]=Math.round(output[i*4+c]*(1-mix)+rgb[c]*mix);
    }
    frames[color]=save(output,w,h,path.join(dir,color+'.png'));
  }
  const bounds=box(parts.panel,w,h,true);
  manifest.formats[fmt]={pixels:[w,h],trim_inches:config.formats[fmt].trim_inches,center_pixel:[(w-1)/2,(h-1)/2],field_bounds:box(parts.field,w,h),top_index_panel_bounds:bounds,
    index_safe_box:[bounds[0]+Math.ceil(12*w/W),bounds[1]+Math.ceil(18*h/H),bounds[2]-Math.ceil(12*w/W),bounds[3]-Math.ceil(18*h/H)],components:files,frames};
  console.log(`Built ${fmt}: two face frames and four reusable masks`);
}
fs.writeFileSync(path.join(dest,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
// Contact sheet is a review aid, not a card asset.
const previews=path.join(root,'docs/design/face-frames-v1-preview.jpg');
const tiles=[];
for(const fmt of Object.keys(manifest.formats))for(const color of Object.keys(palettes)){
  tiles.push('(',path.join(dest,fmt,color+'.png'),'-background','#e3dbcd','-alpha','remove','-resize','225x310','-gravity','north','-extent','260x350','-gravity','south','-font','Arial','-pointsize','13','-fill','#342b24','-annotate','+0+6',fmt+' / '+color,')');
}
magick(['montage',...tiles,'-tile','4x3','-geometry','+6+6','-background','#e3dbcd',previews]);
