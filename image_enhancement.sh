#!/usr/bin/env bash
CURRENT_PATH=`pwd`
SEG_FILE_NUM=30
TARGET_SEG_FILE=${CURRENT_PATH}/rent/rent_txt/rent_apartment_pic.txt
TOTAL_LINE_NUM=`wc -l ${TARGET_SEG_FILE}|awk '{print $1}'`
PER_FILE_LINE_NUM=`expr ${TOTAL_LINE_NUM} / ${SEG_FILE_NUM}`
split -l ${PER_FILE_LINE_NUM} ${TARGET_SEG_FILE}  -d -a 2 ${CURRENT_PATH}/rent/rent_txt/apartment_
FILE_NUM=`ls ${CURRENT_PATH}/rent/rent_txt/apartment_*|wc -l`
FILE=`expr ${FILE_NUM} - 1`
for i in `seq -f "%03g" 0 ${FILE}`;
do
echo ${i}
python ${CURRENT_PATH}/image_enhancement.py \
       --src_file=${CURRENT_PATH}/rent/rent_txt/apartment_${i} \
       --path=${CURRENT_PATH}/rent/pic \
       --exception_log=${CURRENT_PATH}/rent/exception_apartment_${i}.log \
       --process=${CURRENT_PATH}/rent/process_apartment_${i} \
       --problem=${CURRENT_PATH}/rent/problem_apartment${i} &
echo "kill -9 $!" >> kill.sh
done
wait
#cat ${CURRENT_PATH}/${CURRENT_DATE}/predict_result_* >> ${CURRENT_PATH}/${CURRENT_DATE}/${CURRENT_DATE}
