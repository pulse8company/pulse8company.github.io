/* Static pages carry their own language; this handles interactive content only. */
(()=>{
  const dictionary=window.PULSE8_TRANSLATIONS||{};
  const lang=document.documentElement.lang||'en';
  const translate=value=>{
    const text=value.trim();
    return Object.prototype.hasOwnProperty.call(dictionary,text)?value.replace(text,dictionary[text]):value;
  };
  window.pulse8Translate=translate;
  const attrs=['aria-label','alt','title','placeholder'];
  function localize(node){
    if(node.nodeType===3){
      if(node.parentElement?.closest('script,style,.language-switch,textarea,input'))return;
      const value=translate(node.nodeValue);if(value!==node.nodeValue)node.nodeValue=value;
    }else if(node.nodeType===1){
      if(node.matches('script,style,.language-switch,textarea,input'))return;
      for(const attr of attrs){const value=node.getAttribute(attr);if(value){const next=translate(value);if(next!==value)node.setAttribute(attr,next);}}
      for(const child of node.childNodes)localize(child);
    }
  }
  if(lang==='en')return;
  localize(document.body);
  const observer=new MutationObserver(records=>{
    observer.disconnect();
    for(const record of records){
      if(record.type==='childList')for(const node of record.addedNodes)localize(node);
      else localize(record.target);
    }
    observe();
  });
  function observe(){observer.observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:attrs});}
  observe();
})();
