import React, { useEffect, useRef } from 'react';

const MapOverlay = ({ routeData, floorplanSrc }) => {
  const canvasRef = useRef(null);
  
  useEffect(() => {
    if (!routeData || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const img = new Image();
    
    img.onload = () => {
      // Set canvas size to match image
      canvas.width = img.width;
      canvas.height = img.height;
      
      // Draw the floorplan
      ctx.drawImage(img, 0, 0);
      
      // Draw the route
      if (routeData.path && routeData.path.length > 1) {
        ctx.beginPath();
        ctx.strokeStyle = 'red';
        ctx.lineWidth = 3;
        
        // Scale coordinates to match image dimensions
        const scaleX = img.width / 800;  // 800 is the original plot width
        const scaleY = img.height / 650;  // 650 is the original plot height
        
        // Draw the path
        routeData.path.forEach((point, index) => {
          const x = point.x * scaleX;
          const y = point.y * scaleY;
          
          if (index === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        });
        
        ctx.stroke();
        
        // Highlight destination
        const destination = routeData.path[routeData.path.length - 1];
        ctx.beginPath();
        ctx.arc(destination.x * scaleX, destination.y * scaleY, 8, 0, 2 * Math.PI);
        ctx.fillStyle = 'red';
        ctx.fill();
      }
    };
    
    img.src = floorplanSrc;
  }, [routeData, floorplanSrc]);
  
  return (
    <div className="relative w-full h-full">
      <img 
        src={floorplanSrc} 
        alt="Floor Plan" 
        className="absolute top-0 left-0 w-full h-full object-contain"
      />
      <canvas 
        ref={canvasRef}
        className="absolute top-0 left-0 w-full h-full"
      />
    </div>
  );
};

export default MapOverlay;