<derp-table>
    <table>
        <tr>
            <th></th>
            <th each={opts.commit_list}>{hash.substring(0,8)}...</th>
        </tr>
        <tr each={opts.tests} if={active}>
            <td>{name}</td>
            <td each={times}>
                <span if={count}>{mean.toFixed(0)}ms + {count}</span>
                <span if={!count}>NONE</span>
            </td>
        </tr>
    </table>

this.on("mount",function(){
    this.update();
})
</derp-table>

uR.ready(function() {
    uR.math = {};
    uR.math.average = function(numbers) {
        if (!numbers || !numbers.length) { return }
        var total = 0;
        var length = numbers.length || 1;
        for (var i=0;i<numbers.length;i++) { total += numbers[i]; }
        return {
            mean: total/length,
            count: numbers.length,
        }
    }
    function makeChart(x,ys,labels) {
        var canvas = document.createElement("canvas")
        canvas.id="my_chart";
        document.body.appendChild(canvas);
        var ctx = canvas.getContext('2d');
        var datasets = [];
        var colors = [
            'rgb(255, 99, 132)',
            'rgb(0, 99, 132)',
        ];
        uR.forEach(ys,function(y,i) {
            datasets.push({
                label: labels[i],
                borderColor: colors[i],
                data: [0, 10, 5, 2, 20, 30, 45],
            })
        });
            
        var chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: x,
                datasets: datasets,
            },
            options: {}
        });
    }
    uR.ajax({
        url: "/derp/results.json",
        success: function(data) {
            uR.derp = data;
            console.log(data);
        },
    });
});
