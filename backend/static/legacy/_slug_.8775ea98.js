import{S as t,i as s,s as a,a as e,e as n,t as o,h as i,d as l,c as r,b as c,f as h,g as u,j as f,k as m,l as d,q as p,n as g}from"./client.92f71b9d.js";function j(t){let s,a,j,v,b,E,H=t[0].title+"",$=t[0].html+"";return document.title=s=t[0].title,{c(){a=e(),j=n("h1"),v=o(H),b=e(),E=n("div"),this.h()},l(t){i("svelte-1uty71u",document.head).forEach(l),a=r(t),j=c(t,"H1",{});var s=h(j);v=u(s,H),s.forEach(l),b=r(t),E=c(t,"DIV",{class:!0}),h(E).forEach(l),this.h()},h(){f(E,"class","content svelte-emm3f3")},m(t,s){m(t,a,s),m(t,j,s),d(j,v),m(t,b,s),m(t,E,s),E.innerHTML=$},p(t,a){let[e]=a;1&e&&s!==(s=t[0].title)&&(document.title=s),1&e&&H!==(H=t[0].title+"")&&p(v,H),1&e&&$!==($=t[0].html+"")&&(E.innerHTML=$)},i:g,o:g,d(t){t&&l(a),t&&l(j),t&&l(b),t&&l(E)}}}async function v(t){let{params:s}=t;const a=await this.fetch(`blog/${s.slug}.json`),e=await a.json();if(200===a.status)return{post:e};this.error(a.status,e.message)}function b(t,s,a){let{post:e}=s;return t.$$set=t=>{"post"in t&&a(0,e=t.post)},[e]}class E extends t{constructor(t){super(),s(this,t,b,j,a,{post:0})}}export{E as default,v as preload};
