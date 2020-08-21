rm(list=ls())
library(MASS)# 유방암 데이터를 불러오기 위해 기본 데이테셋을 불러오는 
             # MASS 기본패키지를 사용
data("biopsy")#유방암 데이터 불러옴
table(biopsy$class) #class 변수의 빈도수 확인해줌(악성 241, 양성 458)
df <- biopsy #유방암 데이터를 df에 담아줌
df
sum(is.na(df))# 유방암 데이터에 결측값이 총 몇개인 지 확인
install.packages("DMwR") #결측값을 대체하기 위한 함수를 쓰기 
                         #위해 DMwR를 사용
library(DMwR)
df <- centralImputation(df)#결측값을 중앙값 대체하여 준다
df
df$class <- as.character(df$class) #class 변수의 값들을 문자열로 변환 
df$class
df$class[df$class == "malignant"] <- "1" #문자열로 바뀐 악성을 문자열 "1"로 변환
df$class[df$class == "benign"] <- "0" #문자열로 바뀐 양성을 문자열 "0"으로 변환
df$class <- as.factor(df$class) #문자열을 펙터로 변환

t.idx <- sample(1:699, 500) #샘플 총 699 중 1부터 500을 i.idx에 담아줌
df.tr <- df[t.idx,] #훈련데이터로 사용될 500개의 t.idx를 df.tr에 분리 
df.te <- df[-t.idx,] #테스트데이터로 나머지 199개를 분리 

logit <- glm(class ~ V1 + V3 + V6 + V7 + V8 + V9, family = "binomial",data = df.tr[,-1])
#로지스틱 회귀모델을 logit에 생성한다
fitted.values(logit) #모델에 적합된 값인지 fitted()로 확인

coef(logit) #회귀 계수(선형 회귀 모델의 절편이 Intercept으로, 
            #각 변수의 기울기를 보여준다)
summary(logit) #주어진 인자에대한 요약 정보를 보여준다
logit2 <- step(logit,direction = "both")
logit2

#모델 평가
library(ROCR)#ROC 커브를 그리기 위해 사용

prob <- predict(logit, newdata=df.te[,-1], type="response")
prob
prob[prob < 0.5] <- "0"
prob[prob >= 0.5] <- "1"
prob <- as.numeric(prob)
prob

str(df.te$class)
df.te$class <- as.numeric(df.te$class)
df.te 

pr <- prediction(prob, df.te$class) #ROC 커브를 그리기위해 prediction 객체를 생성
                                    #prediction(예측값, 실제값)  
prf <- performance(pr, measure="tpr", x.measure="fpr") #performance(prediction, trp(TP Rate), fpr(FP Rate), rec(recall), acc(Accuracy))
#prediction 객체로부터 performance객체를 생성
#반환값은 performance객체로 plot()을 사용해 그래프를 나타낸다
plot(prf)#그래프 출력

auc <- performance(pr, measure = "auc") #ACU(Area Under the Curve)
auc <- auc@y.values[[1]] #auc 인자를 지정하고 y.values를 본다
auc

# 검증
library(caret)
install.packages("e1071")
confusionMatrix(prob, df.te$class)
prob <- as.factor(prob)
df.te$class <- as.factor(df.te$class)


# 파생변수
install.packages("smbinning")
library(smbinning)
df$class <- as.numeric(df$class) - 1
result=smbinning(df,x="V1",y="class")
result$ivtable
result$iv
pop=smbinning.gen(df,result,"V1_2")
table(pop$V1_2)
summary(pop$V1_2)
str(pop$V1_2)

#result <- smbinning.factor(GermanCredit,x="Duration",y="Class",maxcat = 11)
#result$ivtable








