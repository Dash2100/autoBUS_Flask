function init() {
    $.ajax({
        url: "/status",
        method: "get",
        contentType: "application/json;charset=utf-8",
        success: function (res) {
            console.log(res);
            if (res.status == "on") {
                $("#switch").prop("checked", true);
            }
            else {
                $("#switch").prop("checked", false);
            }
        }
    });
}

function changeStatus(switchVal) {
    if (!switchVal) {
        $("#switch").prop("checked", true);
        Swal.fire({
            title: '你要確定欸？',
            text: "關掉記得要打開",
            icon: 'warning',
            showCancelButton: true,
            focusConfirm: false,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: '關了吧',
            cancelButtonText: '我再想想',
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: "/status",
                    method: "post",
                    contentType: "application/json;charset=utf-8",
                    data: JSON.stringify({ "status": "off" }),
                    success: function (res) {
                        console.log(res);
                        $("#switch").prop("checked", false);
                    }
                })
            }
        })
    }
    else {
        $.ajax({
            url: "/status",
            method: "post",
            contentType: "application/json;charset=utf-8",
            data: JSON.stringify({ "status": "on" }),
            success: function (res) {
                console.log(res);
                $("#switch").prop("checked", true);
            }
        })
    }
}

function manual() {
    Swal.fire({
        title: '手動發送',
        html: '<input id="bus_id" class="swal2-input" placeholder="車號">' +
            '<input id="stu_id" class="swal2-input" placeholder="學號">',
        focusConfirm: false,
        showCancelButton: false,
        confirmButtonText: '送出',
        showDenyButton: true,
        denyButtonText: '送出預設',
        preConfirm: () => {
            return [
                document.getElementById('bus_id').value,
                document.getElementById('stu_id').value
            ]
        }
    }).then((result) => {
        if (result.isConfirmed) {
            if (result.value[0] == "" || result.value[1] == "") {
                Swal.fire({
                    title: '請輸入完整',
                    icon: 'error',
                    confirmButtonText: '確定'
                })
                return;
            }
            $.ajax({
                url: "/manual",
                method: "post",
                contentType: "application/json;charset=utf-8",
                data: JSON.stringify({ "car": result.value[0], "stu_id": result.value[1] }),
                success: function (res) {
                    console.log(res);
                    Swal.fire({
                        title: '送出成功',
                        icon: 'success',
                        confirmButtonText: '確定'
                    })
                }
            })
        } else if (result.isDenied) {
            $.ajax({
                url: "/manual",
                method: "post",
                contentType: "application/json;charset=utf-8",
                data: JSON.stringify({ "car": "default", "stu_id": "default" }),
                success: function (res) {
                    console.log(res);
                    Swal.fire({
                        title: '送出成功',
                        icon: 'success',
                        confirmButtonText: '確定'
                    })
                }
            })
        }
    })
}
