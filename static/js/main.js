var dokuApp = angular.module("dokuApp", []);

dokuApp
.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[{');
    $interpolateProvider.endSymbol('}]}');
  })
.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.headers.common["X-Requested-With"] = 'XMLHttpRequest';
}])
.config(function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
});

dokuApp.controller("DocumentsController", ['$scope', '$http', function($scope, $http) {
    $scope.activeDocument = null;
    $scope.errors = null;
    $scope.modal = UIkit.modal("#document-modal");

    $scope.loadDocument = function(event, documentId) {
        $scope.activeDocument = null;
        var documentsUrl = $(event.target).data('documentUrl');

        $http.get(documentsUrl).success(function(data) {
            $scope.activeDocument = data;
            $scope.modal.show();
        })
    };
    
    $scope.saveForm = function(id) {
        console.log($scope.activeDocument);
        $scope.errors = null;
        $http.post("http://127.0.0.1:8000/document/save/"+id, $scope.activeDocument).success(function(data) {
            if (data.status == "OK") {
                $scope.modal.hide();
                location.reload();
            }
        }).error(function(data) {
            $scope.errors = data;
        });
    };

    $scope.deleteDocument = function(id) {
        console.log(id);
        UIkit.modal.confirm("Oled kindel, et soovid kustutada?", function(){
            $http.delete("http://127.0.0.1:8000/document/delete/" + id).success(function(data) {
                location.reload();
            });
        });
    }
}]);

/*
Katre Metsvahi
 */
dokuApp.controller("NewDocumentController", ['$scope', '$http', function($scope, $http) {
    $http.get("http://127.0.0.1:8000/new_document_form/1").success(function(data) {
        $scope.activeDocument = data;
        $scope.activeDocument.typeSelected = 1;
        $scope.activeDocument.categorySelected = 1;
        $scope.activeDocument.statusSelected = 1;
    });

    $scope.typeUpdate = function() {
        console.log($scope.activeDocument.typeSelected);
        $http.get("http://127.0.0.1:8000/new_document_form/" + $scope.activeDocument.typeSelected).success(function(data) {
            $scope.activeDocument.attributes = data.attributes
        });
    };

    $scope.saveForm = function() {
        $scope.activeDocument.type = $scope.activeDocument.typeSelected;
        $scope.activeDocument.category = $scope.activeDocument.categorySelected;
        $scope.activeDocument.status = $scope.activeDocument.statusSelected;
        $scope.errors = null;
        $http.post("http://127.0.0.1:8000/document/save_new/", $scope.activeDocument).success(function(data) {
            if (data.status == "OK") {
                $scope.modal.hide();
                location.reload();
            }
        }).error(function(data) {
            $scope.errors = data;
        });
    };

}]);

dokuApp.controller("SearchController", ['$scope', '$http', function($scope, $http) {
    $scope.search = {};
}]);