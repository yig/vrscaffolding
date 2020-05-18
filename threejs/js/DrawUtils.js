import {
    LineBasicMaterial,
    PointsMaterial,
    Points,
    BufferGeometry,
    Geometry,
    Vector3,
    Line
} from './three.module.js';

//
// I want to use `draw_line( payload, line_color, line_width )`
// to unify `draw_line` and `draw_curve`, not working.
// error below:
// three.module.js:24015 WebGL: INVALID_FRAMEBUFFER_OPERATION: clear: Cannot render to a XRWebGLLayer framebuffer outside of an XRSession animation frame callback.
//
function draw_line( payload ) {

    if ( payload.length < 2) {
        return;
    }

    var points = [];

    for (let index = 0; index < payload.length; index++) {
        var pt = payload[index];
        var point = new Vector3(pt[0], pt[1], pt[2]);
        points.push( point );
    }

    var geometry = new BufferGeometry().setFromPoints( points );
    var material = new LineBasicMaterial( { color: 0xffff00, linewidth: 1} );

    var line = new Line( geometry, material );

    var dotGeometry = new Geometry();
    dotGeometry.vertices = points;
    var dotMaterial = new PointsMaterial( { color: 0xffff00, size: 5, sizeAttenuation: false } );
    var dot = new Points( dotGeometry, dotMaterial );


    return [line, dot];
}



function draw_curve( payload ) {

    if ( payload.length < 2) {
        return;
    }

    var points = [];

    for (let index = 0; index < payload.length; index++) {
        var pt = payload[index];
        var point = new Vector3(pt[0], pt[1], pt[2]);
        points.push( point );
    }

    var geometry = new BufferGeometry().setFromPoints( points );
    var material = new LineBasicMaterial( { color: 0xffffff, linewidth: 10} );

    var line = new Line( geometry, material );
    return line;
}

function stroke_group_visible( scaffold_strokes, visible) {
    scaffold_strokes.traverse ( function (child) {
        if (child instanceof Line || child instanceof Points) {
               child.visible = visible;
        }
    });
}

export { draw_line, draw_curve, stroke_group_visible };