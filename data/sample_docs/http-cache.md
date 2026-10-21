# HTTP 缓存

HTTP 缓存用来减少重复请求，缩短加载时间。
响应头 Cache-Control 控制缓存行为。
max-age 表示资源可以缓存多少秒。
强缓存命中时浏览器不会发请求，直接读本地副本。
协商缓存会带上 If-None-Match 或 If-Modified-Since 向服务器确认。
服务器返回 304 表示内容没变，可以继续用缓存。
ETag 是内容指纹，内容变了 ETag 就变。
Last-Modified 是最后修改时间，精度只到秒。
内容在一秒内多次变化时，Last-Modified 不太可靠。
no-cache 不是不缓存，它的意思是每次使用前都要向服务器确认。
no-store 才是完全不存，适合含敏感信息的响应。
private 表示只允许浏览器缓存，不允许 CDN 等共享缓存。
public 表示响应可以被任何缓存保存。
must-revalidate 要求缓存过期后必须回源验证。
s-maxage 专门针对共享缓存，优先级高于 max-age。
Vary 声明缓存按哪些请求头区分副本，常用于 Accept-Encoding。
带 Vary: * 的响应几乎无法被有效缓存。
immutable 告诉浏览器在有效期内不必再验证。
静态资源常用文件名带哈希配合长期 max-age 做永久缓存。
缓存失效的常见做法是改文件名或加版本查询参数。
