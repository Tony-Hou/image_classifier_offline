#!/usr/bin/env bash

cd `dirname $0`
CURRENT_PATH=`pwd`
echo $CURRENT_PATH
set +x
CURRENT_DATE=`date "+%Y%m%d"`
#CTIME=`date -d '1 days ago' +%Y-%m-%d`
PT=`date -d '1 days ago' +%Y%m%d`
mkdir ${CURRENT_DATE}
SEG_FILE_NUM=30
##从数仓中查询每天需要计算的未知类型的数据，并导出
TARGET_SEG_FILE=${CURRENT_PATH}/${CURRENT_DATE}/${CURRENT_DATE}.tsv
hive -S -e "
    SELECT
        id,
        parent_id,
        parent_type,
        pic_path,
        origin_url,
        state,
        pic_type
    FROM ods.ods_rpms_rent_house_pic_da
    WHERE (parent_type='2' or parent_type='3') and pic_type='202000000000'
    and state='1' and pt='${PT}000000'" > ${TARGET_SEG_FILE};

TOTAL_LINE_NUM=`wc -l ${TARGET_SEG_FILE}|awk '{print $1}'`
PER_FILE_LINE_NUM=`expr ${TOTAL_LINE_NUM} / ${SEG_FILE_NUM}`
split -l ${PER_FILE_LINE_NUM} ${TARGET_SEG_FILE}  -d -a 2 ${CURRENT_PATH}/${CURRENT_DATE}/classification_
FILE_NUM=`ls ${CURRENT_PATH}/${CURRENT_DATE}/classification_*|wc -l`
FILE=`expr ${FILE_NUM} - 1`
for i in `seq -f "%02g" 0 ${FILE}`;
do
if [ ${i} -lt 15 ]
    then
        python ${CURRENT_PATH}/offline_compute_classification.py --gpu=0 --graph=${CURRENT_PATH}/estate_model_five.pb --process_log=${CURRENT_PATH}/${CURRENT_DATE}/process_da_${i}.log\
        --exception_log=${CURRENT_PATH}/${CURRENT_DATE}/exception_da_${i}.log --result=${CURRENT_PATH}/${CURRENT_DATE}/predict_result_${i}\
        --src_file=${CURRENT_PATH}/${CURRENT_DATE}/classification_${i} &
        echo "kill -9 $!" >> kill.sh
    else
        python ${CURRENT_PATH}/offline_compute_classification.py --gpu=1 --graph=${CURRENT_PATH}/estate_model_five.pb --process_log=${CURRENT_PATH}/${CURRENT_DATE}/process_da_${i}.log\
        --exception_log=${CURRENT_PATH}/${CURRENT_DATE}/exception_da_${i}.log --result=${CURRENT_PATH}/${CURRENT_DATE}/predict_result_${i}\
        --src_file=${CURRENT_PATH}/${CURRENT_DATE}/classification_${i} &
        echo "kill -9 $!" >> kill.sh
fi
done
wait
cat ${CURRENT_PATH}/${CURRENT_DATE}/predict_result_* >> ${CURRENT_PATH}/${CURRENT_DATE}/${CURRENT_DATE}

#计算分类结果存入文件
#导入数仓
hive -e "use rentplat; load data local inpath '${CURRENT_PATH}/${CURRENT_DATE}/${CURRENT_DATE}' overwrite into table rentplat_ods_image_classification_info_da
partition (pt=${PT}000000);"