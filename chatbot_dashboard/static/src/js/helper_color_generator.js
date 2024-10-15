function generateDynamicColors(count) {
  const hueStep = 360 / count;  // Divide the color wheel by the number of colors needed
  return Array.from({ length: count }, (_, i) => {
      const hue = i * hueStep;  // Calculate the hue for each color
      return `hsl(${hue}, 70%, 50%)`;  // Return the HSL color string
  });
}



// function generateDynamicColors(count){
//     const colors=[];
//     for (let i=0;i <count;i++){
//         let color="#" + Math.floor(Math.random()*16777215).toString(16)
//         colors.push(color);
//     }
//
//     return colors
//
// }