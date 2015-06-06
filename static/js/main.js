var dokuApp = angular.module("dokuApp", []);

dokuApp
.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[{');
    $interpolateProvider.endSymbol('}]}');
  })
.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.headers.common["X-Requested-With"] = 'XMLHttpRequest';
}]);

dokuApp.controller("DocumentsController", ['$scope', '$http', function($scope, $http) {
    $scope.activeDocument = null;
    $scope.modal = UIkit.modal("#document-modal");

    $scope.loadDocument = function(event, documentId) {
        $scope.activeDocument = null;
        var documentsUrl = $(event.target).data('documentUrl');

        $http.get(documentsUrl).success(function(data) {
            $scope.activeDocument = data;
            $scope.modal.show();
        })
    }
}]);