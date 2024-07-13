import React,{useEffect, useRef} from 'react';


// Component to support auto scroll at a certain position
// Placing this component on a position will make the screen scroll to that position

const AutoScroll = () => {

    // Referencing the div
    const autoScrollElementRef = useRef();

    // Scrolling to appropriate position whenever component re-renders
    useEffect(() => {
        autoScrollElementRef.current.scrollIntoView();
    })

    // Returning the div for auto-scrolling to it
    return <div ref={autoScrollElementRef}></div>
}

export default AutoScroll;