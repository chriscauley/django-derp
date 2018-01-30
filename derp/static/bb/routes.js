uR.ready(function() {
    uR.addRoutes({
        "/derp/": uR.router.routeElement("bb-toc"),
        "#times": function() { console.log(1);}
    })
});