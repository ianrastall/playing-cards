/** Approved gold-panel backs: native format masters, common geometry, two palette masks.
 * Artistic layout: built-in ImageGen. Registration and export: Node/ImageMagick.
 * node scripts/register_gold_panel.mjs [--apply]
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const revision='gold-panel-v1',sourceDir=path.join(root,'sources/generated/design2-'+revision);
const comp=path.join(root,'sources/components/design2-'+revision),out=path.join(root,'build/design2-'+revision);
const config=JSON.parse(fs.readFileSync(path.join(root,'deck.json'),'utf8'));
const palettes={'prussian-blue':[26,83,117],verdigris:[57,141,114],'madder-lake':[167,52,67],'manganese-violet':[116,80,155],'lamp-black':[33,33,31]};
const fields=Object.fromEntries(Object.entries(palettes).map(([k,v])=>[k,v.map(c=>Math.round(c*.64))]));
const ground=[250,235,215],gold=[227,181,75],margin=23,band=50,inset=margin+band,innerRadius=40,outerRadius=6,cardRadius=3.5/25.4*300;
// Pointwise leaf recoloring, after source sampling. Original masters and geometry stay fixed.
const foliageAdjustment={revision:'olive-leaves-v1',method:'Green-chroma addition with feathered selection; central and satellite medallions excluded.',rgb_chroma_offsets:[1.3,.4,-.2],green_blue_feather:12,green_red_feather:20};
// Bounds were inspected on each independent master. They exclude generated frame ink.
const specs={
  poker:{outer:[34,33,1025,1455],body:[114,112,942,1379],radius:80,roundels:[[263,337,105,99],[795,337,105,99]]},
  bridge:{outer:[39,31,968,1532],body:[118,114,889,1447],radius:75,roundels:[[258,353,101,99],[745,353,101,99]]},
  travel:{outer:[37,37,1011,1463],body:[127,130,923,1363],radius:62,roundels:[[258,334,108,103],[790,334,108,103]]},
  jumbo:{outer:[36,33,1014,1467],body:[108,107,940,1391],radius:28,roundels:[[246,326,94,94],[799,326,94,94]]},
  tarot:{outer:[36,23,904,1634],body:[117,105,824,1546],radius:70,roundels:[[236,362,95,94],[702,362,95,94]]}
};
const clamp=x=>Math.min(1,Math.max(0,x)),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const json=(p,v)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');};
function read(p){const [w,h]=execFileSync('magick',['identify','-format','%w %h',p]).toString().split(' ').map(Number);return {w,h,raw:execFileSync('magick',[p,'-depth','8','rgb:-'],{maxBuffer:64e6})};}
function sample(im,x,y){x=Math.max(0,Math.min(im.w-1,x));y=Math.max(0,Math.min(im.h-1,y));const x0=Math.floor(x),y0=Math.floor(y),x1=Math.min(im.w-1,x0+1),y1=Math.min(im.h-1,y0+1),fx=x-x0,fy=y-y0;return [0,1,2].map(c=>(im.raw[(y0*im.w+x0)*3+c]*(1-fx)+im.raw[(y0*im.w+x1)*3+c]*fx)*(1-fy)+(im.raw[(y1*im.w+x0)*3+c]*(1-fx)+im.raw[(y1*im.w+x1)*3+c]*fx)*fy);}
function findAnchor(im){
  function error(cx,cy){let e=0,n=0;for(let dy=-24;dy<=24;dy+=3)for(let dx=-24;dx<=24;dx+=3){if(dx*dx+dy*dy>576)continue;const a=sample(im,cx+dx,cy+dy),b=sample(im,cx-dx,cy-dy);for(let c=0;c<3;c++){e+=(a[c]-b[c])**2;n++;}}return e/n;}
  let best={x:(im.w-1)/2,y:(im.h-1)/2,error:Infinity};
  for(let dy=-16;dy<=16;dy++)for(let dx=-16;dx<=16;dx++){const x=(im.w-1)/2+dx,y=(im.h-1)/2+dy,e=error(x,y);if(e<best.error)best={x,y,error:e};}
  const coarse={...best};for(let dy=-10;dy<=10;dy++)for(let dx=-10;dx<=10;dx++){const x=coarse.x+dx*.1,y=coarse.y+dy*.1,e=error(x,y);if(e<best.error)best={x,y,error:e};}return best;
}
function inside(x,y,box,r){const [l,t,rr,b]=box;if(x<l||x>rr||y<t||y>b)return false;const dx=Math.max(l+r-x,x-(rr-r),0),dy=Math.max(t+r-y,y-(b-r),0);return dx*dx+dy*dy<=r*r;}
function coverage(x,y,box,r,ss=4){let n=0;for(let j=0;j<ss;j++)for(let i=0;i<ss;i++)if(inside(x+(i+.5)/ss,y+(j+.5)/ss,box,r))n++;return n/(ss*ss);}
function piece(v,edges,values){for(let i=1;i<edges.length;i++)if(v<=edges[i])return values[i-1]+(v-edges[i-1])/(edges[i]-edges[i-1])*(values[i]-values[i-1]);return values.at(-1);}
function reciprocal(a,w,h,ch){if(h%2){const y=Math.floor(h/2);for(let x=0;x<Math.ceil(w/2);x++)for(let c=0;c<ch;c++){const i=(y*w+x)*ch+c,j=(y*w+w-1-x)*ch+c;a[i]=a[j]=Math.round((a[i]+a[j])/2);}}for(let y=Math.ceil(h/2);y<h;y++)for(let x=0;x<w;x++){const i=(y*w+x)*ch,j=((h-1-y)*w+w-1-x)*ch;a.copy(a,i,j,j+ch);}}
function blueAmount(rgb){return clamp((rgb[2]-rgb[1]-1)/12)*clamp((rgb[1]-rgb[0])/20);}
function oliveLeaves(rgb,protectedRegion){
  const [r,g,b]=rgb;
  const amount=protectedRegion?0:Math.round(255*clamp((g-b)/foliageAdjustment.green_blue_feather)*clamp((g-r)/foliageAdjustment.green_red_feather));
  return {rgb:rgb.map((v,c)=>Math.max(0,Math.min(255,v+(g-r)*foliageAdjustment.rgb_chroma_offsets[c]*amount/255))),amount};
}
function nativeBody(fmt,w,h){
  const im=read(path.join(sourceDir,fmt+'-master.png')),spec=specs[fmt],anchor=findAnchor(im),b=spec.body;
  const scale=Math.min((w-2*inset)/(2*Math.max(anchor.x-b[0],b[2]-anchor.x)),(h-2*inset)/(2*Math.max(anchor.y-b[1],b[3]-anchor.y)));
  const plate=Buffer.alloc(w*h*3),mask=Buffer.alloc(w*h),foliageMask=Buffer.alloc(w*h);
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){
    const sx=anchor.x+(x-(w-1)/2)/scale,sy=anchor.y+(y-(h-1)/2)/scale,i=y*w+x;
    let rgb=fields['prussian-blue'],m=1;
    if(inside(sx,sy,b,spec.radius)){
      rgb=sample(im,sx,sy);m=blueAmount(rgb);
      const central=(sx-anchor.x)**2+(sy-anchor.y)**2 < (im.w*.19)**2;
      const roundel=spec.roundels.some(([cx,cy,rx,ry])=>((sx-cx)/rx)**2+((sy-cy)/ry)**2<1);
      if(central||roundel)m=0;
      const foliage=oliveLeaves(rgb,central||roundel);rgb=foliage.rgb;foliageMask[i]=foliage.amount;
    }
    for(let c=0;c<3;c++)plate[i*3+c]=Math.round(rgb[c]);mask[i]=Math.round(m*255);
  }
  reciprocal(plate,w,h,3);reciprocal(mask,w,h,1);reciprocal(foliageMask,w,h,1);
  return {plate,mask,foliageMask,im,spec,geometry:{source:path.relative(root,path.join(sourceDir,fmt+'-master.png')).replaceAll('\\','/'),source_sha256:hash(path.join(sourceDir,fmt+'-master.png')),source_pixels:[im.w,im.h],source_body_bounds:b,source_anchor_pixel:[anchor.x,anchor.y],anchor_fit_mse:anchor.error,uniform_artwork_scale:scale,method:'Independent ImageGen format composition; uniform sampling and translation of the interior, with border reconstruction. No Poker layout resizing.'}};
}
function enlarge(buffer,w,h,nw,nh,ch){return execFileSync('magick',['-size',`${w}x${h}`,'-depth','8',ch===3?'rgb:-':'gray:-','-filter','Lanczos','-resize',`${nw}x${nh}!`,'-depth','8',ch===3?'rgb:-':'gray:-'],{input:buffer,maxBuffer:64e6});}
function compose(body,w,h){
  const plate=Buffer.alloc(w*h*4),borderMask=Buffer.alloc(w*h),fieldMask=Buffer.alloc(w*h);
  const outer=[margin,margin,w-margin,h-margin],inner=[inset,inset,w-inset,h-inset];
  const {im,spec}=body,ob=spec.outer,ib=spec.body;
  for(let y=0;y<Math.ceil(h/2);y++)for(let x=0;x<w;x++){
    const i=y*w+x,oc=coverage(x,y,outer,outerRadius),ic=coverage(x,y,inner,innerRadius);
    let rgb=[...ground],bm=0,fm=0;
    if(oc){
      const sx=piece(x+.5,[margin,inset,w-inset,w-margin],[ob[0]+3,ib[0]-16,ib[2]+16,ob[2]-3]);
      const sy=piece(y+.5,[margin,inset,h-inset,h-margin],[ob[1]+3,ib[1]-16,ib[3]+16,ob[3]-3]);
      const ink=sample(im,sx,sy);
      const inStraightBand=x<inset-4||x>=w-inset+4||y<inset-4||y>=h-inset+4;
      const ornament=inStraightBand?clamp((ink[0]-ink[2]+85)/125):0;
      // Store the unmixed pale-gold ink; the palette mask supplies its background.
      const ring=[247,228,179];
      bm=oc*(1-ornament);rgb=rgb.map((v,c)=>v*(1-oc)+ring[c]*oc);
    }
    if(ic){rgb=rgb.map((v,c)=>v*(1-ic)+body.plate[i*3+c]*ic);bm*=1-ic;fm=ic*body.mask[i]/255;}
    const outerInset=[margin+1.5,margin+1.5,w-margin-1.5,h-margin-1.5];
    const innerInset=[inset+3,inset+3,w-inset-3,h-inset-3];
    const stroke=Math.max(0,oc-coverage(x,y,outerInset,Math.max(0,outerRadius-1.5)),ic-coverage(x,y,innerInset,innerRadius-3));
    if(stroke){rgb=rgb.map((v,c)=>v*(1-stroke)+gold[c]*stroke);bm*=1-stroke;fm*=1-stroke;}
    for(let c=0;c<3;c++)plate[i*4+c]=Math.round(rgb[c]);plate[i*4+3]=Math.round(coverage(x,y,[0,0,w,h],cardRadius,8)*255);
    borderMask[i]=Math.round(bm*255);fieldMask[i]=Math.round(fm*255);
  }
  reciprocal(plate,w,h,4);reciprocal(borderMask,w,h,1);reciprocal(fieldMask,w,h,1);
  return {plate,borderMask,fieldMask,geometry:{...body.geometry,pixels:[w,h],center_pixel:[(w-1)/2,(h-1)/2],outer_margin_px:margin,border_width_px:band,inner_inset_px:inset,outer_bounds:outer,inner_bounds:inner,outer_frame_radius_px:outerRadius,inner_frame_radius_px:innerRadius,corner_radius_mm:3.5}};
}
function save(buf,w,h,dest,ch=4){fs.mkdirSync(path.dirname(dest),{recursive:true});execFileSync('magick',['-size',`${w}x${h}`,'-depth','8',ch===4?'rgba:-':ch===3?'rgb:-':'gray:-','-units','PixelsPerInch','-density','300','-define','png:exclude-chunks=tEXt,zTXt,iTXt,tIME','-define',`png:color-type=${ch===4?6:ch===3?2:0}`,dest],{input:buf,maxBuffer:64e6});}
function paint(p,b,f,color){const a=Buffer.from(p);for(let i=0;i<b.length;i++){const bt=b[i]/255,ft=f[i]/255;for(let c=0;c<3;c++)a[i*4+c]=Math.round(p[i*4+c]*(1-bt-ft)+palettes[color][c]*bt+fields[color][c]*ft);}return a;}
const cards=[],layout={},bodies={},formats=['poker','bridge','travel','jumbo','tarot','european-standard'];
for(const fmt of formats){
  const [w,h]=config.formats[fmt].back_pixels;let body;
  if(fmt==='european-standard'){
    const bridge=bodies.bridge,[bw,bh]=config.formats.bridge.back_pixels;
    body={...bridge,plate:enlarge(bridge.plate,bw,bh,w,h,3),mask:enlarge(bridge.mask,bw,bh,w,h,1),foliageMask:enlarge(bridge.foliageMask,bw,bh,w,h,1),geometry:{method:'Lanczos enlargement of the Bridge artwork plate and field mask, then the common physical border and rounded silhouette are reapplied.',derived_from:'bridge',enlargement:[w/bw,h/bh]}};
    reciprocal(body.plate,w,h,3);reciprocal(body.mask,w,h,1);reciprocal(body.foliageMask,w,h,1);
  }else body=nativeBody(fmt,w,h);
  bodies[fmt]=body;
  save(body.plate,w,h,path.join(comp,fmt,'artwork-plate.png'),3);save(body.mask,w,h,path.join(comp,fmt,'artwork-field-mask.png'),1);
  save(body.foliageMask,w,h,path.join(comp,fmt,'foliage-color-mask.png'),1);
  const {plate,borderMask,fieldMask,geometry}=compose(body,w,h);
  save(plate,w,h,path.join(comp,fmt,'shared-plate.png'));save(borderMask,w,h,path.join(comp,fmt,'border-color-mask.png'),1);save(fieldMask,w,h,path.join(comp,fmt,'field-color-mask.png'),1);
  layout[fmt]={...geometry,components:Object.fromEntries(['artwork-plate','artwork-field-mask','shared-plate','border-color-mask','field-color-mask','foliage-color-mask'].map(n=>[n,{path:path.relative(root,path.join(comp,fmt,n+'.png')).replaceAll('\\','/'),sha256:hash(path.join(comp,fmt,n+'.png'))}]))};
  for(const color of Object.keys(palettes)){
    const a=paint(plate,borderMask,fieldMask,color),rel=`cards/backs/${fmt}/${color}.png`,dest=path.join(out,rel);save(a,w,h,dest);
    const saved=execFileSync('magick',[dest,'-depth','8','rgba:-'],{maxBuffer:64e6});if(!saved.equals(a))throw Error('Lossless export failed: '+rel);
    for(let i=0;i<w*h;i++)for(let c=0;c<4;c++)if(a[i*4+c]!==a[(w*h-1-i)*4+c])throw Error('Half-turn mismatch: '+rel);
    cards.push({id:`design2.back.${fmt}.${color}`,path:rel,format:fmt,color,pixels:[w,h],mode:'RGBA',ppi:300,trim_inches:config.formats[fmt].trim_inches,center_pixel:geometry.center_pixel,sha256:hash(dest),half_turn_exact:true,shared_geometry_exact:true,unchanged_outside_palette_masks:true});
  }
  console.log(`PASS ${fmt}: centered artwork, 50 px frame, five matching dark-field palettes`);
}
const manifest={design:'Design 2',status:'approved',revision,foliage_adjustment:foliageAdjustment,source:{path:path.relative(root,sourceDir).replaceAll('\\','/'),tool:'built-in image_gen'},component_root:path.relative(root,comp).replaceAll('\\','/'),ground_rgb:ground,corner_radius_mm:3.5,palettes,field_palettes:fields,formats,layout,cards};
json(path.join(out,'manifest.json'),manifest);json(path.join(comp,'layout.json'),manifest);
if(process.argv.includes('--apply')){
  execFileSync('python',[path.join(root,'scripts/audit_design2_registration.py'),'--build'],{stdio:'inherit'});
  for(const card of cards){const dest=path.join(root,card.path);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.copyFileSync(path.join(out,card.path),dest);}
  fs.copyFileSync(path.join(out,'manifest.json'),path.join(root,'manifest.json'));
  config.revision=revision;config.renderer='registered-gold-panel-v1';json(path.join(root,'deck.json'),config);
  execFileSync('python',[path.join(root,'scripts/audit_design2_registration.py')],{stdio:'inherit'});
  const repo=path.resolve(root,'../..'),baseline=JSON.parse(fs.readFileSync(path.join(repo,'docs/layout-migration.json'),'utf8'));
  const ledgerPath=path.join(repo,'docs/asset-revisions.json');
  const ledger=fs.existsSync(ledgerPath)?JSON.parse(fs.readFileSync(ledgerPath,'utf8')):{schema_version:1,assets:[]};
  ledger.assets=ledger.assets.filter(a=>!a.path.startsWith('designs/design2/'));
  ledger.assets.push(...cards.map(card=>{
    const p='designs/design2/'+card.path,old=baseline.assets.find(a=>a.path===p);
    if(!old)throw Error('Missing migration baseline: '+p);
    return {path:p,migration_sha256:old.sha256,sha256:card.sha256,revision,foliage_revision:foliageAdjustment.revision,manifest:'designs/design2/manifest.json'};
  }));
  json(ledgerPath,ledger);
  execFileSync('python',[path.join(repo,'scripts/catalog.py'),'--write'],{stdio:'inherit'});
  console.log('Promoted 30 checked Design 2 backs.');
}
