// SankeyChart Component for NexDoc

export const SankeyChart = {
  render(filteredData) {
    const container = document.getElementById('sankeyChartContainer');
    const svg = d3.select('#sankeySvg');
    svg.selectAll('*').remove(); // Clear previous drawings
    
    if (filteredData.length === 0) {
      container.style.display = 'none';
      return;
    }
    container.style.display = 'block';

    const width = Math.max(900, container.clientWidth || 0);
    const height = 500;
    svg.attr('width', width).attr('height', height);

    // 1. Group data into 4 layers: Route -> Type -> College -> Course
    // To prevent rendering thousands of lines, we group minor colleges into "Others"
    const topColleges = Array.from(
      d3.rollup(filteredData, v => d3.sum(v, d => d.seats), d => d.college_name)
    )
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(d => d[0]);

    // Group minor courses into "Others" for visual clarity
    const topCourses = Array.from(
      d3.rollup(filteredData, v => d3.sum(v, d => d.seats), d => d.course)
    )
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(d => d[0]);

    // Preprocess rows to limit college and course complexity
    const processedData = filteredData.map(row => {
      let colName = row.college_name;
      if (!topColleges.includes(colName)) {
        colName = "Other Colleges";
      } else {
        // Shorten name if too long
        if (colName.length > 35) {
          colName = colName.substring(0, 32) + "...";
        }
      }

      let courseName = row.course;
      if (!topCourses.includes(courseName)) {
        courseName = "Other Specialties";
      }

      return {
        route: row.counseling_route === 'MCC' ? 'MCC (Central)' : 'State Portal',
        type: row.college_type + " College",
        college: colName,
        course: courseName,
        seats: row.seats
      };
    });

    // 2. Define layers and compute nodes per layer
    const layers = [
      { key: 'route', label: 'Counselling Route' },
      { key: 'type', label: 'College Type' },
      { key: 'college', label: 'Institution' },
      { key: 'course', label: 'Specialty / Course' }
    ];

    const nodesByLayer = layers.map((layer, layerIdx) => {
      const rolled = d3.rollup(processedData, v => d3.sum(v, d => d.seats), d => d[layer.key]);
      return Array.from(rolled, ([name, seats]) => ({
        id: `${layerIdx}_${name}`,
        name: name,
        seats: seats,
        layer: layerIdx
      })).sort((a, b) => b.seats - a.seats);
    });

    // 3. Compute Node Coordinates
    const columnWidth = 16;
    const layerSpacing = (width - 100) / 3;
    const nodePadding = 12;

    // Scale mapping sum of seats to pixels
    const maxLayerSeats = d3.max(nodesByLayer, layer => d3.sum(layer, n => n.seats)) || 1;
    const maxTotalHeight = height - 100;
    const seatScale = maxTotalHeight / maxLayerSeats;

    nodesByLayer.forEach((layerNodes, layerIdx) => {
      const layerTotalSeats = d3.sum(layerNodes, n => n.seats);
      const totalNodeHeight = layerTotalSeats * seatScale;
      const totalPadding = (layerNodes.length - 1) * nodePadding;
      const startY = (height - (totalNodeHeight + totalPadding)) / 2;

      let currentY = startY;
      layerNodes.forEach(node => {
        node.x = 50 + layerIdx * layerSpacing;
        node.y = currentY;
        node.w = columnWidth;
        node.h = Math.max(8, node.seats * seatScale);
        
        // Tracking offsets for source/target link endpoints
        node.sourceOffset = 0;
        node.targetOffset = 0;

        currentY += node.h + nodePadding;
      });
    });

    // Flatten nodes map for quick ID lookups
    const nodesMap = new Map();
    nodesByLayer.flat().forEach(node => nodesMap.set(node.id, node));

    // 4. Generate Links between layers
    const links = [];

    // Helper to add links between layer N and N+1
    function generateInterLayerLinks(sourceLayerIdx, sourceKey, targetKey) {
      const rolledLinks = d3.rollup(
        processedData,
        v => d3.sum(v, d => d.seats),
        d => d[sourceKey],
        d => d[targetKey]
      );

      for (const [sourceName, targets] of rolledLinks) {
        const sourceNode = nodesMap.get(`${sourceLayerIdx}_${sourceName}`);
        for (const [targetName, seats] of targets) {
          const targetNode = nodesMap.get(`${sourceLayerIdx + 1}_${targetName}`);
          if (sourceNode && targetNode) {
            links.push({
              source: sourceNode,
              target: targetNode,
              seats: seats
            });
          }
        }
      }
    }

    generateInterLayerLinks(0, 'route', 'type');
    generateInterLayerLinks(1, 'type', 'college');
    generateInterLayerLinks(2, 'college', 'course');

    // Pre-calculate offsets for each link so gradients and paths align
    links.forEach(link => {
      const sh = link.seats * seatScale;
      link.sy = link.source.y + link.source.sourceOffset;
      link.ty = link.target.y + link.target.targetOffset;
      link.sh = sh;
      
      link.source.sourceOffset += sh;
      link.target.targetOffset += sh;
    });

    // 5. Draw Links (Gradients / Curved Paths)
    // Setup gradients
    const defs = svg.append('defs');

    links.forEach((link, idx) => {
      const gradId = `sankey-grad-${idx}`;
      const grad = defs.append('linearGradient')
        .attr('id', gradId)
        .attr('gradientUnits', 'userSpaceOnUse')
        .attr('x1', link.source.x + link.source.w)
        .attr('y1', link.sy + link.sh / 2)
        .attr('x2', link.target.x)
        .attr('y2', link.ty + link.sh / 2);

      // Color mapping
      let colorSource = '#00d2ff';
      let colorTarget = '#00f5a0';
      if (link.source.name.includes('State')) colorSource = '#ff7e47';
      if (link.target.name.includes('Deemed')) colorTarget = '#a155ff';

      grad.append('stop').attr('offset', '0%').attr('stop-color', colorSource).attr('stop-opacity', 0.25);
      grad.append('stop').attr('offset', '100%').attr('stop-color', colorTarget).attr('stop-opacity', 0.25);
    });

    // Draw the actual link paths
    const linkGroup = svg.append('g').attr('class', 'links');
    
    linkGroup.selectAll('path')
      .data(links)
      .enter()
      .append('path')
      .attr('class', 'link')
      .attr('d', d => {
        const x0 = d.source.x + d.source.w;
        const y0 = d.sy + d.sh / 2;
        const x1 = d.target.x;
        const y1 = d.ty + d.sh / 2;
        const xi = d3.interpolateNumber(x0, x1);
        const x2 = xi(0.5);

        return `M ${x0} ${y0} C ${x2} ${y0}, ${x2} ${y1}, ${x1} ${y1}`;
      })
      .attr('stroke', (d, i) => `url(#sankey-grad-${i})`)
      .attr('stroke-width', d => Math.max(1, d.seats * seatScale))
      .append('title')
      .text(d => `${d.source.name} ➔ ${d.target.name}\nSeats: ${d.seats}`);

    // 6. Draw Nodes
    const nodeGroup = svg.append('g').attr('class', 'nodes');

    const nodeSelection = nodeGroup.selectAll('.node')
      .data(nodesByLayer.flat())
      .enter()
      .append('g')
      .attr('class', 'node');

    // Draw Rectangles for Nodes
    nodeSelection.append('rect')
      .attr('x', d => d.x)
      .attr('y', d => d.y)
      .attr('width', d => d.w)
      .attr('height', d => d.h)
      .attr('rx', 3)
      .style('fill', d => {
        if (d.layer === 0) return d.name.includes('MCC') ? '#00d2ff' : '#ff7e47';
        if (d.layer === 1) return d.name.includes('Govt') ? '#00d2ff' : d.name.includes('Deemed') ? '#a155ff' : '#ff7e47';
        if (d.layer === 2) return '#00f5a0';
        return '#cbd5e1';
      })
      .style('stroke', 'rgba(0,0,0,0.5)')
      .style('stroke-width', '1px')
      .append('title')
      .text(d => `${d.name}\nTotal Seats: ${d.seats}`);

    // Draw Text Labels
    nodeSelection.append('text')
      .attr('x', d => d.layer === 3 ? d.x - 8 : d.x + d.w + 8)
      .attr('y', d => d.y + d.h / 2)
      .attr('dy', '0.35em')
      .attr('text-anchor', d => d.layer === 3 ? 'end' : 'start')
      .text(d => {
        // Trim labels if too long
        let label = d.name;
        if (label.length > 25) {
          label = label.substring(0, 22) + "...";
        }
        return `${label} (${d.seats})`;
      });
  }
};
