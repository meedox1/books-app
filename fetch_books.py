import subprocess, json, os
def drive_list(q, page_size=100):
    items=[]; token=None
    while True:
        params={"q":q,"pageSize":page_size,"fields":"nextPageToken,files(id,name,mimeType,webViewLink)"}
        if token: params["pageToken"]=token
        out=subprocess.run(["/opt/hatch/bin/hatch_gws_cli","drive","files","list","--params",json.dumps(params)],capture_output=True,text=True)
        d=json.loads(out.stdout)
        items+=d.get("files",[])
        token=d.get("nextPageToken")
        if not token: break
    return items
cats = {
 "روايات": "13nb2NQwqdWjGJw6RLc7y5BjvXDyfw6tO",
 "الفنون والفنون الجميلة والديكور": "16wL9ULx3Oz5UpSnzsGqm6P5t7ZMhCxV3",
 "العلوم التطبيقية ( التكنولوجيا )": "1qbwm-FDZZPKzBrRNroNT1amZo-i-29Js",
 "الدين الإسلامي": "16ezGCKbiVlDuRdekZ6p0oH50EEKy2QZw",
 "الأدب العربي": "0ByYmeaMT6jcLYTZmT3ViX1paZWs",
 "الجغرافيا والتاريخ والعلوم المساعدة": "1d7Nclq2tu7P1FKQe9ES4gWFeHxaz5vZV",
 "العلوم الاجتماعية": "0ByYmeaMT6jcLSWhBZWp5dWtrVm8",
 "اللغات": "0ByYmeaMT6jcLU3hRSi13SVBkbEE",
 "الفلسفة وعلم نفس التخاطر والقوى الخفية وعلم النفس": "15zKmKYKTjkDgFpgJ6FNUoNRPKGAJoo1O",
 "العلوم الطبيعية والرياضيات": "17Bkw57mnIVZbky3dAGK9EohaBtWAstbA",
 "المعارف العامة": "17jUU3vllaUz2F249ZJ6A-vCSlwNY6PYf",
}
result=[]
for cat, fid in cats.items():
    items=drive_list(f"'{fid}' in parents and trashed=false")
    subs=[]
    direct=[]
    for it in items:
        if "folder" in it.get("mimeType",""):
            subitems=drive_list(f"'{it['id']}' in parents and trashed=false")
            books=[{"name":b["name"],"link":b.get("webViewLink")} for b in subitems if b.get("mimeType")=="application/pdf"]
            # if subfolder contains folders (book folders), list one level deeper
            subfolders=[b for b in subitems if "folder" in b.get("mimeType","")]
            for sf in subfolders:
                deep=drive_list(f"'{sf['id']}' in parents and trashed=false")
                for b in deep:
                    if b.get("mimeType")=="application/pdf":
                        books.append({"name":f"{sf['name']} - {b['name']}","link":b.get("webViewLink")})
            subs.append({"name":it["name"],"link":it.get("webViewLink"),"books":books})
        elif it.get("mimeType")=="application/pdf":
            direct.append({"name":it["name"],"link":it.get("webViewLink")})
    result.append({"category":cat,"direct_books":direct,"subcategories":subs})
    print(cat, "direct", len(direct), "subs", len(subs), "books_in_subs", sum(len(s["books"]) for s in subs), flush=True)
with open(os.path.expanduser("~/workspace/books-app/books.json"),"w",encoding="utf-8") as f:
    json.dump(result,f,ensure_ascii=False,indent=2)
print("TOTAL books", sum(len(c["direct_books"])+sum(len(s["books"]) for s in c["subcategories"]) for c in result))
