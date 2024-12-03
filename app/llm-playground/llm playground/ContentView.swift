import SwiftUI
import MarkdownUI

//You are a powerful classifier. Your task is to determine if the query is related to a disaster event. When defining a disaster, it should be assessed based on the scale of the event, the extent of its impact, and the degree of disruption to human life. A “disaster” typically results in infrastructure damage, environmental degradation, casualties, or health threats, and it is a sudden event that requires urgent response and assistance.\n\n[Class]\n1. \"1\" (\"1\" means the query is related to the disaster)\n2. \"0\" (\"0\" means the query is unrelated to the disaster)\n\n[Requirements]\n1. The result should be generated as the JSON format.\n2. There are only 3 'key' in the JSON named \"result\", \"location\", and  \"disaster\".\n3. If there is no location or disaster entity in query, please leave the result empty (like \"\")\n4. Please only generate the JSON, you are forbidden to generate any of your own understanding and explanation.\n5. The classification result must come from [Class]. You cannot create by your own.\n\n\nquery: \"should we be worried that 2025 begins with "wtf"\"\nassistant:


// Delegate class for handling streaming data
class StreamingSessionDelegate: NSObject, URLSessionDataDelegate {
    var dataHandler: ((Data) -> Void)?
    var completionHandler: (() -> Void)?
    
    // Handle data as it arrives
    func urlSession(_ session: URLSession, dataTask: URLSessionDataTask, didReceive data: Data) {
        dataHandler?(data)
    }
    
    // Handle completion
    func urlSession(_ session: URLSession, task: URLSessionTask, didCompleteWithError error: Error?) {
        completionHandler?()
    }
}

struct ChatMessage: Identifiable {
    let id = UUID()
    var message: String
    let isUser: Bool
}

class ChatViewModel: ObservableObject {
    @Published var messages: [ChatMessage] = [
        ChatMessage(message: "Hello! What can I help you today?", isUser: false)
    ]
    @Published var currentMessage: String = ""
    @Published var isMarkdownEnabled: Bool = false
    @Published var isGenerating: Bool = false
    @Published var isOpenAIused: Bool = false
    
    private var dataTask: URLSessionDataTask?
    
    func sendMessage() {
        guard !currentMessage.trimmingCharacters(in: .whitespaces).isEmpty else { return }
        
        let userMessage = ChatMessage(message: currentMessage, isUser: true)
        messages.append(userMessage)
        let inputText = currentMessage
        currentMessage = ""
        
        // Add a placeholder message for the assistant's response
        let botMessage = ChatMessage(message: "", isUser: false)
        messages.append(botMessage)
        
        isGenerating = true
        
        // Call the LLM API
        callLLMAPI(with: inputText, usingOpenAI: isOpenAIused) { responseChunk in
            // Update the placeholder message with the new content
            if let lastIndex = self.messages.firstIndex(where: { $0.id == botMessage.id }) {
                DispatchQueue.main.async {
                    self.messages[lastIndex].message.append(responseChunk)
                }
            }
        }
    }
    
    func stopGeneration() {
        dataTask?.cancel()
        isGenerating = false
    }
    
    private func callLLMAPI(with input: String, usingOpenAI: Bool, completion: @escaping (String) -> Void) {
        // Set up the API endpoint and request
        let url: URL
        var body: [String: Any]
        var request: URLRequest
        
        if usingOpenAI {
            guard let apiURL = URL(string: "https://api.openai.com/v1/chat/completions") else { return }
            url = apiURL
            body = [
                "model": "gpt-4o",
                "messages": [
                    ["role": "user", "content": input]
                ],
                "stream": true
            ]
            // let openAIAPIKey = "" // remember to open this code when you want to run the code & Replace with your actual OpenAI API key
            request = URLRequest(url: url)
            request.addValue("Bearer \(openAIAPIKey)", forHTTPHeaderField: "Authorization")
        } else {
            guard let apiURL = URL(string: "http://localhost:11434/api/generate") else { return }
            url = apiURL
            body = [
                "model": "3B-lora-sft",
                "prompt": input,
                "stream": true
            ]
            request = URLRequest(url: url)
        }
        
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        // Create the delegate
        let delegate = StreamingSessionDelegate()
        let session = URLSession(configuration: .default, delegate: delegate, delegateQueue: nil)
        
        // Handle incoming data
        delegate.dataHandler = { data in
            if let line = String(data: data, encoding: .utf8) {
                // Split lines in case multiple chunks are received
                line.split(separator: "\n").forEach { chunk in
                    var cleanedChunk = chunk.trimmingCharacters(in: .whitespaces)
                    if cleanedChunk.hasPrefix("data:") {
                        cleanedChunk = String(cleanedChunk.dropFirst(5)).trimmingCharacters(in: .whitespaces)
                    }
                    
                    if cleanedChunk == "[DONE]" {
                        print("Stream complete.")
                        DispatchQueue.main.async {
                            self.isGenerating = false
                        }
                        return
                    }
                    
                    guard let jsonData = cleanedChunk.data(using: .utf8),
                          let json = try? JSONSerialization.jsonObject(with: jsonData, options: []) as? [String: Any] else {
                        return
                    }
                    
                    if usingOpenAI {
                        if let choices = json["choices"] as? [[String: Any]],
                           let delta = choices.first?["delta"] as? [String: Any],
                           let content = delta["content"] as? String {
                            DispatchQueue.main.async {
                                completion(content)
                            }
                        }
                    } else {
                        if let output = json["response"] as? String {
                            DispatchQueue.main.async {
                                completion(output)
                            }
                        }
                    }
                }
            }
        }
        
        // Handle completion
        delegate.completionHandler = {
            DispatchQueue.main.async {
                self.isGenerating = false
            }
            print("Request completed.")
        }
        
        // Start the data task
        dataTask = session.dataTask(with: request)
        dataTask?.resume()
    }
}

struct ChatView: View {
    @StateObject private var viewModel = ChatViewModel()
    
    var body: some View {
        VStack {
            Toggle("Enable Markdown", isOn: $viewModel.isMarkdownEnabled)
                .padding()
            Toggle("Use OpenAI API", isOn: $viewModel.isOpenAIused)
            
            ScrollViewReader { scrollViewProxy in
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 10) {
                        ForEach(viewModel.messages) { message in
                            HStack(alignment: .top, spacing: 10) {
                                if !message.isUser {
                                    // Assistant avatar
                                    Image("assistant_icon")
                                        .resizable()
                                        .frame(width: 40, height: 40)
                                        .foregroundColor(.gray)
                                }
                                
                                VStack(alignment: message.isUser ? .trailing : .leading) {
                                    if message.isUser {
                                        Spacer()
                                    }
                                    
                                    if viewModel.isMarkdownEnabled {
                                        Markdown(message.message)
                                            .padding()
                                            .background(Color.gray.opacity(0.2))
                                            .foregroundColor(.black)
                                            .cornerRadius(12)
                                            .frame(maxWidth: .infinity, alignment: message.isUser ? .trailing : .leading)
                                    } else {
                                        Text(message.message)
                                            .padding()
                                            .background(message.isUser ? Color.blue.opacity(0.8) : Color.gray.opacity(0.2))
                                            .foregroundColor(message.isUser ? .white : .black)
                                            .cornerRadius(12)
                                            .frame(maxWidth: .infinity, alignment: message.isUser ? .trailing : .leading)
                                    }
                                    
                                    if !message.isUser {
                                        Spacer()
                                    }
                                }
                                
                                if message.isUser {
                                    // User avatar
                                    Image("personal_icon")
                                        .resizable()
                                        .frame(width: 40, height: 40)
                                        .foregroundColor(.blue)
                                }
                            }
                            .id(message.id)
                        }
                    }
                    .padding(.horizontal)
                    .padding(.top, 10)
                    .onChange(of: viewModel.messages.count) { _ in
                        if let lastMessage = viewModel.messages.last {
                            withAnimation {
                                scrollViewProxy.scrollTo(lastMessage.id, anchor: .bottom)
                            }
                        }
                    }
                }
            }
            
            HStack {
                TextField("Type a message...", text: $viewModel.currentMessage)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .padding(.horizontal)
                    .onSubmit {
                        viewModel.sendMessage()
                    }
                
                if viewModel.isGenerating {
                    Button(action: viewModel.stopGeneration) {
                        Text("Stop")
                            .padding(.horizontal, 10)
                            .padding(.vertical, 5)
                            .background(Color.red)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                    .padding(.trailing)
                    .transition(.opacity)
                } else {
                    Button(action: viewModel.sendMessage) {
                        Image(systemName: "paperplane.fill")
                            .font(.system(size: 24))
                            .foregroundColor(.blue)
                    }
                    .padding(.trailing)
                }
            }
            .padding(.bottom, 10)
        }
    }
}

struct ContentView: View {
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

#Preview {
    ContentView()
}
