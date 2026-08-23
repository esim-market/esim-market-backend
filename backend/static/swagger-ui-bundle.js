/* Small self-hosted documentation viewer used for bootstrap environments. */
window.SwaggerUIBundle=function(o){fetch(o.url).then(function(r){return r.json()}).then(function(spec){var el=document.querySelector(o.dom_id||"#swagger-ui");el.innerHTML="<h2>"+(spec.info&&spec.info.title||"API")+"</h2><p>OpenAPI "+(spec.openapi||"")+'</p><pre>'+JSON.stringify(spec,null,2)+"</pre>"})};
