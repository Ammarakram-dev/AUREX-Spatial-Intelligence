(() => {
"use strict";
const START="/api/camera/start", STOP="/api/camera/stop", STREAM="/api/camera/stream";
let cameraOn=false, button=null;
function feed(){return document.getElementById("aurex-camera-feed")||document.querySelector(".aurex-camera-feed");}
function build(){
 if(document.getElementById("aurex-camera-control")){button=document.getElementById("aurex-camera-control");return;}
 button=document.createElement("button"); button.id="aurex-camera-control"; button.type="button";
 button.innerHTML='<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#7d8997;margin-right:9px"></span><span>CAMERA OFF</span>';
 button.style.cssText="position:fixed!important;right:24px!important;bottom:24px!important;z-index:2147483647!important;width:170px!important;height:52px!important;border:1px solid rgba(100,210,255,.5)!important;border-radius:14px!important;background:#101821!important;color:#f4f8ff!important;font-family:Arial,sans-serif!important;font-size:13px!important;font-weight:700!important;letter-spacing:2px!important;cursor:pointer!important;pointer-events:auto!important;display:block!important;";
 document.body.appendChild(button);
 button.onclick=()=>cameraOn?off():on();
}
function update(){if(button)button.querySelector("span:last-child").textContent=cameraOn?"CAMERA ON":"CAMERA OFF";}
async function on(){
 build(); button.disabled=true;
 try{
  const r=await fetch(START,{method:"POST",cache:"no-store"}), d=await r.json();
  if(!d.camera)throw new Error(d.message||"Camera unavailable");
  const f=feed(); if(f){f.style.display="block";f.src=STREAM+"?t="+Date.now();}
  cameraOn=true;update();
 }catch(e){console.error(e);alert("Camera could not be started.\n\n"+e.message);}
 finally{button.disabled=false;}
}
async function off(){
 build(); const f=feed(); if(f){f.src="";f.removeAttribute("src");f.style.display="none";}
 cameraOn=false;update();
 try{await fetch(STOP,{method:"POST",cache:"no-store"});}catch(e){console.warn(e);}
}
window.AUREXCamera={on,off,state:()=>cameraOn};
function init(){build();off();}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();