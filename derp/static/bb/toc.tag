<bb-toc>
    <table>
        <tr each={ data.groups }>
            <td>{ name }</td>
            <td>{ count }</td>
            <td each={ runs }></td>
        </tr>
    </table>

    this.on("mount",function() {
        uR.ajax({
            url: "/derp/groups.json",
            success: function(data,response) { this.data = data },
            tag: this,
        });
    });
</bb-toc>