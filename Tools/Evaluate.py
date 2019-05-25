import os
import fileinput
import collections
import numpy as np
from collections import defaultdict

class EvaluateModel(object):
    def __init__(self, rel_set_path = None, HMM = False):
        # TDT2 path ../Corpus/TDT2/AssessmentTrainSet/AssessmentTrainSet.txt
        # HMMTrainingSet path ../Corpus/TDT2/Train/QDRelevanceTDT2_forHMMOutSideTrain
        if rel_set_path == None:
            self.answerTraingSet_path = "../Corpus/TDT2/AssessmentTrainSet/AssessmentTrainSet.txt"
        else:
            self.answerTraingSet_path = rel_set_path
        self.answer = self.__getAssessment(HMM)
        self.APs = []
        self.num_docs = 2265
        
    def __getAssessment(self, HMM):
        answerTraingSetDict = defaultdict(list)
        answerTraingSet_path = self.answerTraingSet_path
        with open(answerTraingSet_path, 'r') as f:
            # read content of query document (doc, content)
            title = ""
            for line in f.readlines():
                result = line.split()              
                if len(result) == 0:
                    continue
                if len(result) > 1:
                    if not HMM:
                        title = result[2]
                    else:
                        title = result[1]
                    continue

                answerTraingSetDict[title].append(result[0])
                
        return answerTraingSetDict

    def getAset(self):
        return self.answer
    # result : list [(doc, point)]
    # answer_list : list [(doc)]
    def __avePrecision(self, result, q_key, atPos = None):
        iterative = 0.
        count = 0.
        precision = 0.
        answer = self.answer[q_key]
        if atPos == None:
            atPos = len(answer)
    
        for doc_name in result:
            iterative += 1
            if count == atPos: break
            if doc_name in answer:
                count += 1
                precision += count / iterative
         
        precision /= len(answer)
        return precision

    def DCG(self, result, q_key):
        d_cumul_gain = np.zeros(self.num_docs)
        answer = self.answer[q_key]
        
        if result[0] in answer:
            d_cumul_gain[0] = 1. / np.log2(2)
        else:
            d_cumul_gain[0] = 0.
            
        for s_idx in range(1, self.num_docs):
            c_idx = s_idx + 2
            gain = 0.
            if s_idx < len(result):
                doc_name = result[s_idx]
                if doc_name in answer:
                    gain = 1.
            d_cumul_gain[s_idx] = gain / np.log2(c_idx) + d_cumul_gain[s_idx - 1]
            
        return d_cumul_gain
        
    def mAP(self, query_docs_dict):
        mAP = 0.
        cumulAP = 0.
        for q_key, doc_list in query_docs_dict.items():
            AP = self.__avePrecision(doc_list, q_key)
            cumulAP += AP
            self.APs.append([q_key, AP])
        mAP = cumulAP / len(query_docs_dict.keys())
        return mAP
    
    def precisionAtK(self, query_docs_dict, atPos):
        mPAK = 0.
        cumulAP = 0.
        num_qry = len(list(query_docs_dict.keys()))
        for q_key, doc_list in query_docs_dict.items():
            pAK = self.__avePrecision(docs_list, q_key, atPos)
            cumulAP += pAK
        mPAK = cumulAP / num_qry
        return mPAK
    
    def NDCGAtK(self, query_docs_dict, atPos = None):
        mPAK = 0.
        first_qry_key = list(query_docs_dict.keys())[0]
        num_qry = len(list(query_docs_dict.keys()))
        num_results = len(query_docs_dict[first_qry_key])
        dcg = np.zeros(num_results)
        idcg = np.zeros(num_results)
        
        for q_key, doc_list in query_docs_dict.items():
            dcg += self.DCG(doc_list, q_key)
            idcg += self.DCG(self.answer[q_key], q_key)
        # average
        dcg /= num_qry 
        idcg /= num_qry
        ndcg = dcg / idcg
        
        if atPos == None:
            return ndcg
        else:
            return ndcg[atPos]
        
if __name__ == "__main__":
    eva = EvaluateModel()
