/** Register one floral master and shared frame; palette changes never move pixels.
 * Run: node scripts/register_design2.mjs
 * Artistic edits: built-in ImageGen. Exact registration/export: Node/ImageMagick.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const sourceDir=path.join(root,'sources/generated/design2-registered-v1');
const componentDir=path.join(root,'sources/components/design2-registered-v1');
const output=path.join(root,'build/design2-registered-v1');
const sourcePath=path.join(sourceDir,'floral-master.png');
const config=JSON.parse(fs.readFileSync(path.join(root,'deck.json'),'utf8'));
const formats=['poker','bridge','european-standard','jumbo','travel','tarot'];
const palettes={'prussian-blue':[26,83,117],verdigris:[57,141,114],'madder-lake':[167,52,67],'manganese-violet':[116,80,155],'lamp-black':[33,33,31]};
const colors=Object.keys(palettes),ground=[250,235,215],radius=3.5/25.4*300;
const [sw,sh]=execFileSync('magick',['identify','-format','%w %h',sourcePath]).toString().split(' ').map(Number);
if(sw!==1060||sh!==1484)throw new Error('Unexpected master geometry');
const raw=execFileSync('magick',[sourcePath,'-depth','8','rgb:-'],{maxBuffer:32e6});
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const sourceHash=hash(sourcePath),clamp=v=>Math.min(1,Math.max(0,v));
const writeJSON=(p,v)=>fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');
fs.mkdirSync(componentDir,{recursive:true});fs.mkdirSync(output,{recursive:true});
function sample(x,y,c){
  x=Math.max(0,Math.min(sw-1,x));y=Math.max(0,Math.min(sh-1,y));
  const x0=Math.floor(x),y0=Math.floor(y),x1=Math.min(sw-1,x0+1),y1=Math.min(sh-1,y0+1),fx=x-x0,fy=y-y0;
  return (raw[(y0*sw+x0)*3+c]*(1-fx)+raw[(y0*sw+x1)*3+c]*fx)*(1-fy)+(raw[(y1*sw+x0)*3+c]*(1-fx)+raw[(y1*sw+x1)*3+c]*fx)*fy;
}
function centerError(cx,cy){
  let error=0,n=0;
  // Compare the central floral disk under a half-turn, independently of its frame.
  for(let dy=-32;dy<=32;dy+=2)for(let dx=-32;dx<=32;dx+=2){
    if(dx*dx+dy*dy>32*32)continue;
    for(let c=0;c<3;c++){const d=sample(cx+dx,cy+dy,c)-sample(cx-dx,cy-dy,c);error+=d*d;n++;}
  }
  return error/n;
}
let best={x:530,y:736,error:Infinity};
for(let y=728;y<=744;y++)for(let x=522;x<=538;x++){
  const e=centerError(x,y);if(e<best.error)best={x,y,error:e};
}
const coarse={...best};
for(let yi=-20;yi<=20;yi++)for(let xi=-20;xi<=20;xi++){
  const x=coarse.x+xi*.05,y=coarse.y+yi*.05,e=centerError(x,y);
  if(e<best.error)best={x,y,error:e};
}
const anchor=[best.x,best.y],anchorEdge=anchor.map(x=>x+.5);
console.log('Measured central floral anchor:',anchor);
function piece(v,edges,values){
  for(let i=1;i<edges.length;i++)if(v<=edges[i])return values[i-1]+(v-edges[i-1])/(edges[i]-edges[i-1])*(values[i]-values[i-1]);
  return values.at(-1);
}
function alpha(x,y,w,h){
  if(x>=radius&&x<w-radius||y>=radius&&y<h-radius)return 255;
  let count=0;
  for(let oy=0;oy<8;oy++)for(let ox=0;ox<8;ox++){
    const px=x+(ox+.5)/8,py=y+(oy+.5)/8;
    const dx=Math.max(radius-px,px-(w-radius),0),dy=Math.max(radius-py,py-(h-radius),0);
    if(dx*dx+dy*dy<=radius*radius)count++;
  }
  return Math.round(255*count/64);
}
function reciprocal(a,w,h,channels){
  if(h%2){const y=Math.floor(h/2);for(let x=0;x<Math.ceil(w/2);x++)for(let c=0;c<channels;c++){
    const i=(y*w+x)*channels+c,j=(y*w+w-1-x)*channels+c;
    a[i]=a[j]=Math.round((a[i]+a[j])/2);
  }}
  for(let y=Math.ceil(h/2);y<h;y++)for(let x=0;x<w;x++){
    const i=(y*w+x)*channels,j=((h-1-y)*w+w-1-x)*channels;
    a.copy(a,i,j,j+channels);
  }
}
function prepare(w,h){
  const plate=Buffer.alloc(w*h*4),mask=Buffer.alloc(w*h);
  const u=w/750,margin=23*u,band=50*u,inner=margin+band;
  const sxScale=(w-2*inner)/812,centralStart=h/2-184*sxScale;
  const xs=Array.from({length:w},(_,x)=>piece(x+.5,[0,margin,inner,w/2,w-inner,w-margin,w],[0,32,124,anchorEdge[0],936,1028,1060])-.5);
  for(let y=0;y<Math.ceil(h/2);y++){
    const sy=piece(y+.5,[0,margin,inner,centralStart,h/2],[0,25,110,anchorEdge[1]-184,anchorEdge[1]])-.5;
    for(let x=0;x<w;x++){
      const sx=xs[x],i=(y*w+x)*4,rgb=[0,1,2].map(c=>sample(sx,sy,c));
      const nearPaper=Math.min(1,clamp((rgb[0]-231)/12),clamp((rgb[1]-221)/13),clamp((rgb[2]-196)/14));
      for(let c=0;c<3;c++)plate[i+c]=Math.round(rgb[c]*(1-nearPaper)+ground[c]*nearPaper);
      plate[i+3]=alpha(x,y,w,h);
      const dx=Math.max(200-sx,sx-860,0),dy=Math.max(182-sy,0);
      const interior=sx>=130&&sx<=930&&sy>=112&&dx*dx+dy*dy<=4900;
      const amount=interior?0:clamp((rgb[2]-rgb[0])/70)*clamp((rgb[2]-rgb[1])/22);
      mask[y*w+x]=Math.round(amount*255);
      // The outside trim margin is one uniform paper plate, without generated hairlines.
      if(x+.5<margin-2*u||x+.5>w-margin+2*u||y+.5<margin-2*u){
        for(let c=0;c<3;c++)plate[i+c]=ground[c];mask[y*w+x]=0;
      }
    }
  }
  reciprocal(plate,w,h,4);reciprocal(mask,w,h,1);
  return {plate,mask,geometry:{pixels:[w,h],center_pixel:[(w-1)/2,(h-1)/2],center_edge:[w/2,h/2],outer_margin_px:margin,border_width_px:band,inner_inset_px:inner,outer_bounds:[margin,margin,w-margin,h-margin],inner_bounds:[inner,inner,w-inner,h-inner],central_source_anchor_pixel:anchor,central_source_anchor_edge:anchorEdge,central_vertical_scale:sxScale}};
}
function save(a,w,h,dest,channels=4){
  fs.mkdirSync(path.dirname(dest),{recursive:true});
  execFileSync('magick',['-size',`${w}x${h}`,'-depth','8',channels===4?'rgba:-':'gray:-','-units','PixelsPerInch','-density','300','-define',`png:color-type=${channels===4?6:0}`,dest],{input:a,maxBuffer:32e6});
}
function paint(plate,mask,palette){
  const a=Buffer.from(plate);
  for(let i=0;i<mask.length;i++)if(mask[i]){const t=mask[i]/255;for(let c=0;c<3;c++)a[i*4+c]=Math.round(plate[i*4+c]*(1-t)+palette[c]*t);}
  return a;
}
const cards=[],layout={};
for(const fmt of formats){
  const [w,h]=config.formats[fmt].back_pixels,{plate,mask,geometry}=prepare(w,h);
  save(plate,w,h,path.join(componentDir,fmt,'shared-plate.png'));
  save(mask,w,h,path.join(componentDir,fmt,'border-color-mask.png'),1);
  layout[fmt]={...geometry,shared_plate_sha256:hash(path.join(componentDir,fmt,'shared-plate.png')),border_mask_sha256:hash(path.join(componentDir,fmt,'border-color-mask.png'))};
  for(const color of colors){
    const a=paint(plate,mask,palettes[color]),rel=`backs/${fmt}/${color}.png`,dest=path.join(output,rel);
    save(a,w,h,dest);
    const saved=execFileSync('magick',[dest,'-depth','8','rgba:-'],{maxBuffer:32e6});
    if(!saved.equals(a))throw new Error(`Roundtrip mismatch: ${rel}`);
    for(let i=0;i<w*h;i++)for(let c=0;c<4;c++){
      if(a[i*4+c]!==a[(w*h-1-i)*4+c])throw new Error(`Half-turn mismatch: ${rel}`);
      if((!mask[i]||c===3)&&a[i*4+c]!==plate[i*4+c])throw new Error(`Shared plate moved: ${rel}`);
    }
    cards.push({id:`design2.back.${fmt}.${color}`,path:rel,format:fmt,color,pixels:[w,h],mode:'RGBA',ppi:300,trim_inches:config.formats[fmt].trim_inches,center_pixel:geometry.center_pixel,sha256:hash(dest),half_turn_exact:true,shared_geometry_exact:true,unchanged_outside_border_mask:true,lossless_roundtrip:true});
  }
  console.log(`PASS ${fmt}: five palettes, one exact plate and mask`);
}
if(hash(sourcePath)!==sourceHash)throw new Error('Source changed');
const manifest={design:'Design 2',status:'registered provisional winner',revision:'floral-registration-v1',source:{path:path.relative(root,sourcePath).replaceAll('\\','/'),sha256:sourceHash,tool:'built-in image_gen'},registration:{method:'Measured central floral disk using a 0.05-pixel half-turn least-squares search, then mapped the artwork anchor to each canvas center before reciprocal construction.',source_anchor_pixel:anchor,fit_mean_squared_error:best.error},ground_rgb:ground,corner_radius_mm:3.5,palettes,formats,layout,cards};
writeJSON(path.join(output,'manifest.json'),manifest);
writeJSON(path.join(componentDir,'layout.json'),manifest);
fs.copyFileSync(path.join(sourceDir,'prompts.json'),path.join(output,'prompts.json'));
fs.copyFileSync(path.join(componentDir,'viewer.html'),path.join(output,'index.html'));
fs.copyFileSync(path.join(componentDir,'README.md'),path.join(output,'README.md'));
console.log(`Created ${cards.length} registered backs: ${output}`);
