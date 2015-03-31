var width = 960,
    height = 500

var svg = d3.select("#tree-container").append("svg")
    .attr("width", width)
    .attr("height", height);

var color = d3.scale.category20();

var force = d3.layout.force()
    .gravity(.05)
    .distance(100)
    .charge(-100)
    .size([width, height]);

function make_tree(json_url) {
  d3.json(json_url, function(error, json) {

    force
        .nodes(json.nodes)
        .links(json.links)
        .on("tick", tick)
        .start();

    var link = svg.selectAll(".link")
        .data(json.links)
      .enter().append("line")
        .attr("class", "link");

    var node = svg.selectAll(".node")
        .data(json.nodes)
      .enter().append("g")
        .attr("class", "node")
        .call(force.drag);

    node.append("circle")
        .attr("class", "node")
        .attr("r", 5)
        .style("fill", function(d) { return color(d.dept); })

    node.append("text")
        .attr("dx", 12)
        .attr("dy", ".35em")
        .attr("class", function(d) {
          return d.prime ? "label prime" : "label";
        })
        .text(function(d) {
          return d.dept + " " + d.number
        });

    function tick(e) {

      // Push sources up and targets down to form a weak tree.
      var k = 6 * e.alpha;
      json.links.forEach(function(d, i) {
        d.source.y -= k;
        d.target.y += k;
      });

      link.attr("x1", function(d) { return d.source.x; })
          .attr("y1", function(d) { return d.source.y; })
          .attr("x2", function(d) { return d.target.x; })
          .attr("y2", function(d) { return d.target.y; });

      node.attr("transform", function(d) {
          return "translate(" + d.x + "," + d.y + ")";
      });
    }

  });
}
