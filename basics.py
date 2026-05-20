import cv2
import numpy as np
import face_recognition

# Step 1: Load Images and Convert to RGB
# নিশ্চিত করুন যে 'images/basic' ফোল্ডারে 'Elon Musk.jpg' এবং 'Elon Musk Test.jpg' আছে।
# অথবা আপনার নিজের ছবি ব্যবহার করুন।
imgElon = face_recognition.load_image_file('images/basic/Elon Musk.jpg')
imgElon = cv2.cvtColor(imgElon, cv2.COLOR_BGR2RGB)

imgElonTest = face_recognition.load_image_file('images/basic/Elon Musk Test.jpg')
imgElonTest = cv2.cvtColor(imgElonTest, cv2.COLOR_BGR2RGB)

# Optionally, load Bill Gates test image to see false match
imgBillGatesTest = face_recognition.load_image_file('images/basic/Bill Gates Test.jpg')
imgBillGatesTest = cv2.cvtColor(imgBillGatesTest, cv2.COLOR_BGR2RGB)

# Step 2: Find Face Locations and Encodings
faceLocElon = face_recognition.face_locations(imgElon)[0]
encodeElon = face_recognition.face_encodings(imgElon, [faceLocElon])[0]

faceLocElonTest = face_recognition.face_locations(imgElonTest)[0]
encodeElonTest = face_recognition.face_encodings(imgElonTest, [faceLocElonTest])[0]

faceLocBillGatesTest = face_recognition.face_locations(imgBillGatesTest)[0]
encodeBillGatesTest = face_recognition.face_encodings(imgBillGatesTest, [faceLocBillGatesTest])[0]

# Draw rectangle around face for visualization
cv2.rectangle(imgElon, (faceLocElon[3], faceLocElon[0]), (faceLocElon[1], faceLocElon[2]), (255, 0, 255), 2)
cv2.rectangle(imgElonTest, (faceLocElonTest[3], faceLocElonTest[0]), (faceLocElonTest[1], faceLocElonTest[2]), (255, 0, 255), 2)
cv2.rectangle(imgBillGatesTest, (faceLocBillGatesTest[3], faceLocBillGatesTest[0]), (faceLocBillGatesTest[1], faceLocBillGatesTest[2]), (255, 0, 255), 2)


# Step 3: Compare Faces and Find Distance
# Comparing Elon Musk with Elon Musk Test
resultsElon = face_recognition.compare_faces([encodeElon], encodeElonTest)
faceDisElon = face_recognition.face_distance([encodeElon], encodeElonTest)
print(f"Elon vs Elon Test - Results: {resultsElon}, Distance: {round(faceDisElon[0], 2)}")

# Comparing Elon Musk with Bill Gates Test
resultsBill = face_recognition.compare_faces([encodeElon], encodeBillGatesTest)
faceDisBill = face_recognition.face_distance([encodeElon], encodeBillGatesTest)
print(f"Elon vs Bill Gates Test - Results: {resultsBill}, Distance: {round(faceDisBill[0], 2)}")

# Display results on images
cv2.putText(imgElonTest, f'{resultsElon[0]} {round(faceDisElon[0], 2)}', (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
cv2.putText(imgBillGatesTest, f'{resultsBill[0]} {round(faceDisBill[0], 2)}', (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)


cv2.imshow('Elon Musk', imgElon)
cv2.imshow('Elon Musk Test', imgElonTest)
cv2.imshow('Bill Gates Test', imgBillGatesTest) # Display Bill Gates test image
cv2.waitKey(0)
cv2.destroyAllWindows()