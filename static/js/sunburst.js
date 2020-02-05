function toHHMM(min_num) {
    var hours   = Math.floor(min_num / 60);
    var minutes = Math.floor((min_num - (hours * 60)));

    if (hours   < 10) {hours   = "0"+hours;}
    if (minutes < 10) {minutes = "0"+minutes;}
    return hours+':'+minutes;
}

async function make_chart() {
    let data = await d3.json("/static/data/clock.json", function(error, data) {});

    width = 975;
    radius = width / 2;
    format = d3.format(",d");
    partition = data => d3.partition()
        .size([2 * Math.PI, radius])(d3.hierarchy(data)
                                     .sum(d => d.value)
                                     .sort((a, b) => b.value - a.value));

    sum_all = data => {
        if (data.children != null) {
            return data.children.map(sum_all).reduce((a, b) => a + b, (typeof data.value !== 'undefined' ? data.value: 0));
        }
        return data.value;
    };

    d3.select("#time_worked")
        .text(() => {
            let d = sum_all(data);
            return toHHMM(d);
        });

    make_label = d => {
        return d.data.name.substring(0,18)
            .concat((d.data.name.length > 18 ? '...': ''));
    };
    make_hour_label = d => toHHMM(d.value);

    arc = d3.arc()
        .startAngle(d => d.x0)
        .endAngle(d => d.x1)
        .padAngle(d => Math.min((d.x1 - d.x0) / 2, 0.005))
        .padRadius(radius / 2)
        .innerRadius(d => d.y0)
        .outerRadius(d => d.y1 - 1);
    color = d3.scaleOrdinal(d3.quantize(d3.interpolateRainbow, data.children.length + 1));

    function autoBox() {
        const {x, y, width, height} = this.getBBox();
        return [x, y, width, height];
    };
    const root = partition(data);
    const svg = d3.select("svg")
          .style("max-width", "80%")
          .style("height", "auto")
          .style("font", "9px sans-serif")
          .style("margin", "5px");

    svg.append("g")
        .attr("fill-opacity", 0.6)
        .selectAll("path")
        .data(root.descendants().filter(d => d.depth))
        .enter().append("path")
        .attr("fill", d => { while (d.depth > 1) d = d.parent; return color(d.data.name); })
        .attr("d", arc)
        .append("title")
        .text(d => `${d.ancestors().map(d => d.data.name).reverse().join("/")}\n${format(d.value)}`);

    let all_texts = svg.append("g")
        .attr("pointer-events", "none")
        .attr("text-anchor", "middle").selectAll("text");

    all_texts.data(root.descendants().filter(d => d.depth && ((d.y0 + d.y1) / 2 * (d.x1 - d.x0) > 10) && ((d.y0 + d.y1) / 2 * (d.x1 - d.x0) < 25)))
        .enter()
        .append("text")
        .attr("transform", function(d) {
            const x = (d.x0 + d.x1) / 2 * 180 / Math.PI;
            const y = (d.y0 + d.y1) / 2;
            return `rotate(${x - 90}) translate(${y},0) rotate(${x < 180 ? 0 : 180})`;
        })
        .attr("dy", "0.35em")
        .append("tspan")
        .text(d => make_label(d));

    all_texts.data(root.descendants().filter(d => d.depth && (d.y0 + d.y1) / 2 * (d.x1 - d.x0) > 25))
        .enter()
        .append("text")
        .attr("transform", function(d) {
            const x = (d.x0 + d.x1) / 2 * 180 / Math.PI;
            const y = (d.y0 + d.y1) / 2;
            return `rotate(${x - 90}) translate(${y},0) rotate(${x < 180 ? 0 : 180})`;
        })
        .attr("dy", "0.35em")
        .append("tspan")
        .text(d => make_label(d))
        .append("tspan")
        .text(d => make_hour_label(d))
        .attr("dy", "1.2em")
        .attr("x", "0");

    svg.attr("viewBox", autoBox);
}

make_chart();
