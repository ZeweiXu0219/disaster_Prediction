import SwiftUI
import MarkdownUI

struct ChatMessage: Identifiable {
    let id = UUID()
    let message: String
    let isUser: Bool
}

struct ChatView: View {
    @State private var messages: [ChatMessage] = [
        ChatMessage(message: "Hello! How can I help you today?", isUser: false)
    ]
    @State private var currentMessage: String = ""

    var body: some View {
        VStack {
            ScrollViewReader { scrollViewProxy in
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 10) {
                        ForEach(messages) { message in
                            HStack {
                                if message.isUser {
                                    Spacer()
                                    Text(message.message)
                                        .padding()
                                        .background(Color.blue.opacity(0.8))
                                        .foregroundColor(.white)
                                        .cornerRadius(12)
                                        .frame(maxWidth: .infinity, alignment: .trailing)
                                } else {
                                    Markdown(message.message)
                                        .padding()
                                        .background(Color.gray.opacity(0.2))
                                        .foregroundColor(.black)
                                        .cornerRadius(12)
                                        .frame(maxWidth: .infinity, alignment: .leading)
                                    Spacer()
                                }
                            }
                        }
                    }
                    .padding(.horizontal)
                    .onChange(of: messages.count) {
                        withAnimation {
                            scrollViewProxy.scrollTo(messages.last?.id, anchor: .bottom)
                        }
                    }
                }
            }

            HStack {
                TextField("Type a message...", text: $currentMessage)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .padding(.horizontal)

                Button(action: sendMessage) {
                    Image(systemName: "paperplane.fill")
                        .font(.system(size: 24))
                        .foregroundColor(.blue)
                }
                .padding(.trailing)
            }
            .padding(.bottom, 10)
        }
    }

    private func sendMessage() {
        guard !currentMessage.trimmingCharacters(in: .whitespaces).isEmpty else { return }
        
        let userMessage = ChatMessage(message: currentMessage, isUser: true)
        messages.append(userMessage)
        let inputText = currentMessage
        currentMessage = ""
        
        // Call the LLM API
        callLLMAPI(with: inputText) { response in
            let botResponse = ChatMessage(message: response, isUser: false)
            messages.append(botResponse)
        }
    }
    
    private func callLLMAPI(with input: String, completion: @escaping (String) -> Void) {
        // Set up the API endpoint and request
        // openAI API: https://api.openai.com/v1/chat/completions
        // ollama default API: http://localhost:11434/api/generate
        guard let url = URL(string: "http://localhost:11434/api/generate") else { return }
        //let openAIAPIKey = ""
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        //request.addValue("Bearer \(openAIAPIKey)", forHTTPHeaderField: "Authorization")
        
        // Set up the request body with the input text
        // openAI format
        //let body: [String: Any] = [
        //    "model": "gpt-4o-mini",
        //    "messages": [
        //        ["role": "user", "content": input]
        //    ]
        //]
        
        //ollama format
        let body: [String: Any] = [
            "model": "llama3.2:3b",
            "prompt": input,
            "stream":false
        ]
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        // Perform the API request
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("Error: \(error.localizedDescription)")
                return
            }
            
//            guard let data = data,
//                  let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
//                  let choices = json["choices"] as? [[String: Any]],
//                  let message = choices.first?["message"] as? [String: Any],
//                  let output = message["content"] as? String else {
//                print("Failed to parse response")
//                return
            guard let data = data,
                  let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                  let output = json["response"] as? String else {
                print("Failed to parse response")
                return
            }
            
            // Pass the response output to the completion handler
            DispatchQueue.main.async {
                completion(output)
            }
        }.resume()
    }
}

struct ContentView: View {
    struct ContentView_Previews: PreviewProvider {
        static var previews: some View {
            ContentView()
        }
    }
    var body: some View {
        ChatView()
    }
}

struct ChatApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
