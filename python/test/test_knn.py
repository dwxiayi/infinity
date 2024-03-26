# Copyright(C) 2023 InfiniFlow, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pytest

from common import common_values
import infinity
import infinity.index as index
from infinity.errors import ErrorCode
from infinity.common import ConflictType

from utils import copy_data


class TestKnn:

    def test_version(self):
        print(infinity.__version__)

    @pytest.mark.parametrize("check_data", [{"file_name": "tmp_20240116.csv",
                                             "data_dir": common_values.TEST_TMP_DIR}], indirect=True)
    def test_knn(self, check_data):
        infinity_obj = infinity.connect(common_values.TEST_REMOTE_HOST)
        # assert infinity_obj
        #
        # infinity
        #
        db_obj = infinity_obj.get_database("default")

        db_obj.drop_table("fix_tmp_20240116", conflict_type=ConflictType.Ignore)
        table_obj = db_obj.create_table("fix_tmp_20240116", {
            "variant_id": "varchar",
            "gender_vector": "vector,4,float",
            "color_vector": "vector,4,float",
            "category_vector": "vector,4,float",
            "tag_vector": "vector,4,float",
            "other_vector": "vector,4,float",
            "query_is_recommend": "varchar",
            "query_gender": "varchar",
            "query_color": "varchar",
            "query_price": "float"
        }, ConflictType.Error)

        test_csv_dir = "/tmp/infinity/test_data/tmp_20240116.csv"
        if not check_data:
            copy_data("tmp_20240116.csv")
        print("import:", test_csv_dir, " start!")
        table_obj.import_data(test_csv_dir, None)

        # true
        # search
        # table_obj = db_obj.get_table("fix_tmp_20240116")
        # res = table_obj.output(["variant_id"]).to_df()

        # true
        # res = table_obj.output(["variant_id", "query_price"]).knn('gender_vector', [1.0] * 768, "float", "ip",
        #                                                           10).to_pl()
        # print(res)

        # true
        res = table_obj.output(["variant_id", "_row_id"]).knn(
            "gender_vector", [1.0] * 4, "float", "ip", 10).to_pl()
        print(res)

        # FIXME
        # res = table_obj.output(["variant_id", "query_is_recommend", "query_gender", "query_color", "query_price"]).knn(
        #     "gender_vector", [1.0] * 4, "float", "ip", 3).to_pl()

        # print(res)

    def test_insert_multi_column(self):
        infinity_obj = infinity.connect(common_values.TEST_REMOTE_HOST)

        with pytest.raises(Exception, match=r".*value count mismatch*"):
            db_obj = infinity_obj.get_database("default")
            db_obj.drop_table("test_insert_multi_column", conflict_type=ConflictType.Ignore)
            table = db_obj.create_table("test_insert_multi_column", {
                "variant_id": "varchar",
                "gender_vector": "vector,4,float",
                "color_vector": "vector,4,float",
                "category_vector": "vector,4,float",
                "tag_vector": "vector,4,float",
                "other_vector": "vector,4,float",
                "query_is_recommend": "varchar",
                "query_gender": "varchar",
                "query_color": "varchar",
                "query_price": "float"
            }, ConflictType.Error)
            table.insert([{"variant_id": "123",
                           "gender_vector": [1.0] * 4,
                           "color_vector": [2.0] * 4,
                           "category_vector": [3.0] * 4,
                           "tag_vector": [4.0] * 4,
                           "other_vector": [5.0] * 4,
                           "query_is_recommend": "ok",
                           "query_gender": "varchar",
                           # "query_color": "red",
                           "query_price": 1.0
                           }])

    # knn various column name
    @pytest.mark.parametrize("check_data", [{"file_name": "tmp_20240116.csv",
                                             "data_dir": common_values.TEST_TMP_DIR}], indirect=True)
    @pytest.mark.parametrize("column_name", [pytest.param("variant_id", marks=pytest.mark.xfail),
                                             "gender_vector",
                                             "color_vector",
                                             pytest.param("query_price", marks=pytest.mark.xfail),
                                             # pytest.param(1, marks=pytest.mark.xfail),
                                             # pytest.param(2.2, marks=pytest.mark.xfail),
                                             # pytest.param("!@#/\#$ ## #$%  @#$^", marks=pytest.mark.xfail),
                                             ])
    def test_various_vector_column_name(self, get_infinity_db, check_data, column_name):
        db_obj = get_infinity_db
        db_obj.drop_table("test_various_vector_column_name", conflict_type=ConflictType.Ignore)
        table_obj = db_obj.create_table("test_various_vector_column_name", {
            "variant_id": "varchar",
            "gender_vector": "vector,4,float",
            "color_vector": "vector,4,float",
            "category_vector": "vector,4,float",
            "tag_vector": "vector,4,float",
            "other_vector": "vector,4,float",
            "query_is_recommend": "varchar",
            "query_gender": "varchar",
            "query_color": "varchar",
            "query_price": "float"
        }, ConflictType.Error)
        if not check_data:
            copy_data("tmp_20240116.csv")
        test_csv_dir = "/tmp/infinity/test_data/tmp_20240116.csv"
        table_obj.import_data(test_csv_dir, None)
        res = table_obj.output(["variant_id", "_row_id"]).knn(column_name, [1.0] * 4, "float", "ip", 2).to_pl()
        print(res)

    @pytest.mark.parametrize("check_data", [{"file_name": "tmp_20240116.csv",
                                             "data_dir": common_values.TEST_TMP_DIR}], indirect=True)
    @pytest.mark.parametrize("embedding_data", [
        pytest.param("variant_id", marks=pytest.mark.xfail(reason="Invalid embedding data")),
        pytest.param("gender_vector", marks=pytest.mark.xfail(reason="Invalid embedding data")),
        pytest.param(1, marks=pytest.mark.xfail(reason="Invalid embedding data")),
        pytest.param(2.4, marks=pytest.mark.xfail(reason="Invalid embedding data")),
        pytest.param([1] * 3, marks=pytest.mark.xfail(reason="Invalid embedding data")),
        pytest.param((1, 2, 3), marks=pytest.mark.xfail(reason="Invalid embedding data")),
        pytest.param({"c": "12"}, marks=pytest.mark.xfail(reason="Invalid embedding data")),
        [1] * 4,
        (1, 2, 3, 4),
    ])
    def test_various_embedding_data(self, get_infinity_db, check_data, embedding_data):
        db_obj = get_infinity_db
        db_obj.drop_table("test_various_embedding_data", conflict_type=ConflictType.Ignore)
        table_obj = db_obj.create_table("test_various_embedding_data", {
            "variant_id": "varchar",
            "gender_vector": "vector,4,float",
            "color_vector": "vector,4,float",
            "category_vector": "vector,4,float",
            "tag_vector": "vector,4,float",
            "other_vector": "vector,4,float",
            "query_is_recommend": "varchar",
            "query_gender": "varchar",
            "query_color": "varchar",
            "query_price": "float"
        }, ConflictType.Error)
        if not check_data:
            copy_data("tmp_20240116.csv")
        test_csv_dir = "/tmp/infinity/test_data/tmp_20240116.csv"
        table_obj.import_data(test_csv_dir, None)
        res = table_obj.output(["variant_id", "_row_id"]).knn("gender_vector", embedding_data, "float", "ip", 2).to_pl()
        print(res)

    @pytest.mark.parametrize("check_data", [{"file_name": "tmp_20240116.csv",
                                             "data_dir": common_values.TEST_TMP_DIR}], indirect=True)
    @pytest.mark.parametrize("embedding_data", [
        [1] * 4,
        [1.0] * 4,
    ])
    @pytest.mark.parametrize("embedding_data_type", [
        ("int", False),
        ("float", True),
        pytest.param(1, marks=pytest.mark.xfail(reason="Invalid embedding 1.0 type")),
        pytest.param(2.2, marks=pytest.mark.xfail(reason="Invalid embedding 1.0 type")),
        pytest.param("#@!$!@", marks=pytest.mark.xfail(reason="Invalid embedding 1.0 type")),
    ])
    def test_various_embedding_data_type(self, get_infinity_db, check_data, embedding_data, embedding_data_type):
        db_obj = get_infinity_db
        db_obj.drop_table("test_various_embedding_data_type", conflict_type=ConflictType.Ignore)
        table_obj = db_obj.create_table("test_various_embedding_data_type", {
            "variant_id": "varchar",
            "gender_vector": "vector,4,float",
            "color_vector": "vector,4,float",
            "category_vector": "vector,4,float",
            "tag_vector": "vector,4,float",
            "other_vector": "vector,4,float",
            "query_is_recommend": "varchar",
            "query_gender": "varchar",
            "query_color": "varchar",
            "query_price": "float"
        }, ConflictType.Error)
        if not check_data:
            copy_data("tmp_20240116.csv")
        test_csv_dir = "/tmp/infinity/test_data/tmp_20240116.csv"
        table_obj.import_data(test_csv_dir, None)
        if embedding_data_type[1]:
            res = table_obj.output(["variant_id"]).knn("gender_vector", embedding_data, embedding_data_type[0], "ip",
                                                       2).to_pl()
            print(res)
        else:
            with pytest.raises(Exception, match="ERROR:3032*"):
                res = table_obj.output(["variant_id"]).knn("gender_vector", embedding_data, embedding_data_type[0],
                                                           "ip",
                                                           2).to_pl()

    @pytest.mark.parametrize("check_data", [{"file_name": "tmp_20240116.csv",
                                             "data_dir": common_values.TEST_TMP_DIR}], indirect=True)
    @pytest.mark.parametrize("embedding_data", [
        [1] * 4,
        [1.0] * 4,
    ])
    @pytest.mark.parametrize("embedding_data_type", [
        # ("int", False),
        ("float", True),
    ])
    @pytest.mark.parametrize("distance_type", [
        ("l2", True),
        ("cosine", False),
        ("ip", True),
        ("hamming", False),
    ])
    def test_various_distance_type(self, get_infinity_db, check_data, embedding_data, embedding_data_type,
                                   distance_type):
        db_obj = get_infinity_db
        db_obj.drop_table("test_various_distance_type", conflict_type=ConflictType.Ignore)
        table_obj = db_obj.create_table("test_various_distance_type", {
            "variant_id": "varchar",
            "gender_vector": "vector,4,float",
            "color_vector": "vector,4,float",
            "category_vector": "vector,4,float",
            "tag_vector": "vector,4,float",
            "other_vector": "vector,4,float",
            "query_is_recommend": "varchar",
            "query_gender": "varchar",
            "query_color": "varchar",
            "query_price": "float"
        }, ConflictType.Error)
        if not check_data:
            copy_data("tmp_20240116.csv")
        test_csv_dir = "/tmp/infinity/test_data/tmp_20240116.csv"
        table_obj.import_data(test_csv_dir, None)
        if distance_type[1] and embedding_data_type[1]:
            res = table_obj.output(["variant_id"]).knn("gender_vector", embedding_data, embedding_data_type[0],
                                                       distance_type[0],
                                                       2).to_pl()
            print(res)
        else:
            with pytest.raises(Exception, match="ERROR:3032*"):
                res = table_obj.output(["variant_id"]).knn("gender_vector", embedding_data, embedding_data_type[0],
                                                           distance_type[0],
                                                           2).to_pl()

    @pytest.mark.parametrize("check_data", [{"file_name": "tmp_20240116.csv",
                                             "data_dir": common_values.TEST_TMP_DIR}], indirect=True)
    @pytest.mark.parametrize("topn", [
        (2, True),
        (10, True),
        (0, False, "ERROR:3014*"),
        (-1, False, "ERROR:3014*"),
        (1.1, False, "Invalid topn"),
        ("test", False, "Invalid topn"),
        ({}, False, "Invalid topn"),
        ((), False, "Invalid topn"),
        ([1] * 4, False, "Invalid topn"),
    ])
    def test_various_topn(self, get_infinity_db, check_data, topn):
        db_obj = get_infinity_db
        db_obj.drop_table("test_various_topn", conflict_type=ConflictType.Ignore)
        table_obj = db_obj.create_table("test_various_topn", {
            "variant_id": "varchar",
            "gender_vector": "vector,4,float",
            "color_vector": "vector,4,float",
            "category_vector": "vector,4,float",
            "tag_vector": "vector,4,float",
            "other_vector": "vector,4,float",
            "query_is_recommend": "varchar",
            "query_gender": "varchar",
            "query_color": "varchar",
            "query_price": "float"
        }, ConflictType.Error)
        if not check_data:
            copy_data("tmp_20240116.csv")
        test_csv_dir = "/tmp/infinity/test_data/tmp_20240116.csv"
        table_obj.import_data(test_csv_dir, None)
        if topn[1]:
            res = table_obj.output(["variant_id"]).knn("gender_vector", [1] * 4, "float", "l2", topn[0]).to_pl()
            print(res)
        else:
            with pytest.raises(Exception, match=topn[2]):
                res = table_obj.output(["variant_id"]).knn("gender_vector", [1] * 4, "float", "l2", topn[0]).to_pl()

    @pytest.mark.parametrize("check_data", [{"file_name": "pysdk_test_knn.csv",
                                             "data_dir": common_values.TEST_TMP_DIR}], indirect=True)
    @pytest.mark.parametrize("index_column_name", ["gender_vector",
                                                   "color_vector",
                                                   "category_vector",
                                                   "tag_vector",
                                                   "other_vector"])
    @pytest.mark.parametrize("knn_column_name", ["gender_vector",
                                                 "color_vector",
                                                 "category_vector",
                                                 "tag_vector",
                                                 "other_vector"])
    @pytest.mark.parametrize("index_distance_type", ["l2", "ip"])
    @pytest.mark.parametrize("knn_distance_type", ["l2", "ip"])
    def test_with_index_before(self, get_infinity_db, check_data, index_column_name, knn_column_name,
                        index_distance_type, knn_distance_type):
        db_obj = get_infinity_db
        db_obj.drop_table("test_with_index", ConflictType.Ignore)
        table_obj = db_obj.create_table("test_with_index", {
            "variant_id": "varchar",
            "gender_vector": "vector,4,float",
            "color_vector": "vector,4,float",
            "category_vector": "vector,4,float",
            "tag_vector": "vector,4,float",
            "other_vector": "vector,4,float",
            "query_is_recommend": "varchar",
            "query_gender": "varchar",
            "query_color": "varchar",
            "query_price": "float"
        }, ConflictType.Error)
        if not check_data:
            copy_data("pysdk_test_knn.csv")
        test_csv_dir = "/tmp/infinity/test_data/pysdk_test_knn.csv"
        table_obj.import_data(test_csv_dir, None)
        res = table_obj.create_index("my_index",
                                     [index.IndexInfo(index_column_name,
                                                      index.IndexType.Hnsw,
                                                      [
                                                          index.InitParameter(
                                                              "M", "16"),
                                                          index.InitParameter(
                                                              "ef_construction", "50"),
                                                          index.InitParameter(
                                                              "ef", "50"),
                                                          index.InitParameter(
                                                              "metric", index_distance_type)
                                                      ])], ConflictType.Error)

        assert res.error_code == ErrorCode.OK

        res = table_obj.output(["variant_id"]).knn(knn_column_name, [1] * 4, "float", knn_distance_type, 5).to_pl()
        print(res)

    @pytest.mark.parametrize("check_data", [{"file_name": "pysdk_test_knn.csv",
                                             "data_dir": common_values.TEST_TMP_DIR}], indirect=True)
    @pytest.mark.parametrize("index_column_name", ["gender_vector",
                                                   "color_vector",
                                                   "category_vector",
                                                   "tag_vector",
                                                   "other_vector"])
    @pytest.mark.parametrize("knn_column_name", ["gender_vector",
                                                 "color_vector",
                                                 "category_vector",
                                                 "tag_vector",
                                                 "other_vector"])
    @pytest.mark.parametrize("index_distance_type", ["l2", "ip"])
    @pytest.mark.parametrize("knn_distance_type", ["l2", "ip"])
    def test_with_index_after(self, get_infinity_db, check_data,
                        index_column_name, knn_column_name,
                        index_distance_type, knn_distance_type):
        db_obj = get_infinity_db
        db_obj.drop_table("test_with_index", ConflictType.Ignore)
        table_obj = db_obj.create_table("test_with_index", {
            "variant_id": "varchar",
            "gender_vector": "vector,4,float",
            "color_vector": "vector,4,float",
            "category_vector": "vector,4,float",
            "tag_vector": "vector,4,float",
            "other_vector": "vector,4,float",
            "query_is_recommend": "varchar",
            "query_gender": "varchar",
            "query_color": "varchar",
            "query_price": "float"
        }, ConflictType.Error)
        if not check_data:
            copy_data("pysdk_test_knn.csv")
        test_csv_dir = "/tmp/infinity/test_data/pysdk_test_knn.csv"
        table_obj.import_data(test_csv_dir, None)
        res = table_obj.output(["variant_id"]).knn(knn_column_name, [1.0] * 4, "float", knn_distance_type, 5).to_pl()
        print(res)
        res = table_obj.create_index("my_index",
                                     [index.IndexInfo(index_column_name,
                                                      index.IndexType.Hnsw,
                                                      [
                                                          index.InitParameter(
                                                              "M", "16"),
                                                          index.InitParameter(
                                                              "ef_construction", "50"),
                                                          index.InitParameter(
                                                              "ef", "50"),
                                                          index.InitParameter(
                                                              "metric", index_distance_type)
                                                      ])], ConflictType.Error)

        assert res.error_code == ErrorCode.OK


