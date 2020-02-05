function saveSvg(svgEl, name) {
    svgEl.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    var svgData = svgEl.outerHTML;
    var preface = '<?xml version="1.0" standalone="no"?>\r\n';
    var svgBlob = new Blob([preface, svgData],
                           {type:"image/svg+xml;charset=utf-8"});
    var svgUrl = URL.createObjectURL(svgBlob);
    var downloadLink = document.createElement("a");
    downloadLink.href = svgUrl;
    downloadLink.download = name;
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}
window.onload = function() {
    //get svg source.
    var button = document.createElement("button");
    button.id = "export_button";
    button.textContent = "Export as SVG";
    button.addEventListener("click", function () {
        //get svg element.
        var svg2 = document.getElementsByTagName('svg');
        saveSvg(svg2[0], 'save.svg');
    });

    document.body.appendChild(button);
}
