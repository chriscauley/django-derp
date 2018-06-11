uR.ready(function() {
    uR.addRoutes({
        "/derp/": uR.router.routeElement("bb-groups"),
        "#groups-(\\d+)": uR.router.routeElement("bb-group-detail"),
        "#times": function() { console.log(1);}
    })
});